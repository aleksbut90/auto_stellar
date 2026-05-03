"""
Bot Recorder - записывает скриншоты окна игры и действия пользователя
Формат датасета:
  dataset/
    session_XXX/
      frames/  (скриншоты)
      actions.json  (нажатые клавиши с таймстампами)
"""

import os
import time
import json
import threading
from datetime import datetime
from PIL import Image
import keyboard
import mouse
import numpy as np
import pydirectinput
import win32gui
import win32api
import win32con
import win32ui


class BotRecorder:
    def __init__(self, status_callback=None):
        self.recording = False
        self.stop_event = threading.Event()
        self.status_callback = status_callback

        self.fps = 10
        self.game_window_rect = None  # (x, y, width, height)
        self.capture_rect = None  # реальные координаты для захвата
        self.session_dir = None
        self.frames_dir = None
        self.actions = []
        self.start_time = None
        self.main_window_ref = None  # ссылка на главное окно для Z-order

        # Буфер кадров в памяти
        self._frame_buffer = []  # [(filename_bytes, img_bytes), ...]
        self._buffer_lock = threading.Lock()

        # Для отслеживания нажатий клавиш
        self._key_listener = None
        self._mouse_move_active = False

    def set_game_window_rect(self, rect):
        """Установить прямоугольник окна игры. rect = (x, y, width, height)"""
        # Сохраняем полный rect для логирования
        self.game_window_rect = rect

        # Но для захвата скриншота используем client area (без рамок окна)
        # Пытаемся получить клиентскую область через win32
        try:
            import win32gui
            import win32con

            hwnd = win32gui.WindowFromPoint((rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
            if hwnd:
                # Получаем клиентскую область (без заголовка и рамок)
                client_rect = win32gui.GetClientRect(hwnd)
                client_to_window = win32gui.ClientToScreen(hwnd, (0, 0))

                # Client area = (left, top, width, height)
                self.capture_rect = (client_to_window[0], client_to_window[1],
                                     client_rect[2], client_rect[3])
            else:
                self.capture_rect = rect
        except Exception:
            self.capture_rect = rect

    def start(self, output_dir="dataset", main_window_hwnd=None):
        """Начать запись"""
        if not self.capture_rect:
            if self.status_callback:
                self.status_callback("❌ Сначала подключись к игре")
            return False

        # Убираем topmost и отправляем на задний план
        if main_window_hwnd:
            self.main_window_ref = main_window_hwnd
            try:
                # Убираем флаг topmost (HWND_NOTOPMOST = -2)
                win32gui.SetWindowPos(main_window_hwnd, -2, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                # Отправляем на задний план (HWND_BOTTOM = 1)
                win32gui.SetWindowPos(main_window_hwnd, 1, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
            except:
                pass

        # Создаём папку сессии
        session_num = self._get_next_session_num(output_dir)
        self.session_dir = os.path.join(output_dir, f"session_{session_num:03d}")
        self.frames_dir = os.path.join(self.session_dir, "frames")
        os.makedirs(self.frames_dir, exist_ok=True)

        # Очищаем буфер
        self._frame_buffer = []

        self.actions = []
        self.start_time = time.time()
        self.recording = True
        self.stop_event.clear()

        # Запуск потока записи скриншотов
        self._screenshot_thread = threading.Thread(target=self._record_screenshots, daemon=True)
        self._screenshot_thread.start()

        # Запуск слушателя клавиш и мыши
        self._start_key_listener()

        if self.status_callback:
            self.status_callback(f"🔴 Запись начата: {self.session_dir}")

        return True

    def stop(self):
        """Остановить запись"""
        if not self.recording:
            return

        self.recording = False
        self.stop_event.set()

        # Остановка слушателя клавиш и мыши
        self._stop_key_listener()

        # Сохранение буфера кадров на диск
        self._flush_frame_buffer()

        # Сохранение actions.json
        self._save_actions()

        # Возвращаем главное окно на передний план
        if self.main_window_ref:
            try:
                # HWND_TOP = 0 — вернуть на передний план
                win32gui.SetWindowPos(self.main_window_ref, 0, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                win32gui.SetForegroundWindow(self.main_window_ref)
            except:
                pass

        if self.status_callback:
            self.status_callback(f"✅ Запись сохранена: {self.session_dir} ({len(self.actions)} действий)")

    def is_recording(self):
        return self.recording

    # -----------------------------
    # Запись скриншотов
    # -----------------------------
    def _record_screenshots(self):
        """Цикл записи скриншотов окна игры (mss - очень быстрый)"""
        import mss

        interval = 1.0 / self.fps
        frame_count = 0

        # Разрешение для сохранения (уменьшаем для экономии места)
        TARGET_WIDTH = 1280
        TARGET_HEIGHT = 720

        x, y, w, h = self.capture_rect

        with mss.mss() as sct:
            monitor = {"top": y, "left": x, "width": w, "height": h}

            while not self.stop_event.is_set():
                try:
                    # Захват через mss (очень быстро)
                    sct_img = sct.grab(monitor)

                    # Конвертация в PIL Image
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

                    # Уменьшение разрешения до 1280x720
                    img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.BILINEAR)

                    # Сохранение в JPEG в буфер (RAM)
                    import io
                    buf = io.BytesIO()
                    img.save(buf, "JPEG", quality=85)
                    img_bytes = buf.getvalue()

                    frame_name = f"frame_{frame_count:05d}.jpg"
                    with self._buffer_lock:
                        self._frame_buffer.append((frame_name, img_bytes))
                    frame_count += 1

                except Exception as e:
                    if self.status_callback:
                        self.status_callback(f"⚠️ Ошибка скриншота: {e}")

                # Ждём до следующего кадра
                self.stop_event.wait(interval)

    # -----------------------------
    # Отслеживание клавиш
    # -----------------------------
    def _start_key_listener(self):
        """Запуск слушателя нажатий клавиш + мыши"""
        # Клавиатура
        def on_key(event):
            if not self.recording:
                return

            if event.event_type == keyboard.KEY_DOWN:
                timestamp = time.time() - self.start_time
                action = {
                    "time": round(timestamp, 3),
                    "type": "keydown",
                    "key": event.name
                }
                self.actions.append(action)

        try:
            self._key_listener = keyboard.hook(on_key)
            self._key_listener_active = True
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"⚠️ Не удалось отследить клавиши (нужны права админа): {e}")

        # Мышь — один обработчик для кликов И движений
        self._last_mouse_pos = None
        self._last_mouse_time = 0

        def on_mouse(event):
            if not self.recording:
                return

            now = time.time()

            # Движение мыши
            if isinstance(event, mouse.MoveEvent):
                # Записываем не чаще 10 раз/сек чтобы не спамить
                if now - self._last_mouse_time < 0.1:
                    return

                # Проверяем что позиция изменилась
                if self._last_mouse_pos == (event.x, event.y):
                    return

                self._last_mouse_pos = (event.x, event.y)
                self._last_mouse_time = now

                rel_x = event.x - self.capture_rect[0]
                rel_y = event.y - self.capture_rect[1]

                timestamp = now - self.start_time
                action = {
                    "time": round(timestamp, 3),
                    "type": "mouse_move",
                    "x": rel_x,
                    "y": rel_y
                }
                self.actions.append(action)

            # Клик мыши — получаем текущую позицию через mouse.get_position()
            elif isinstance(event, mouse.ButtonEvent):
                try:
                    mx, my = mouse.get_position()
                    rel_x = mx - self.capture_rect[0]
                    rel_y = my - self.capture_rect[1]
                except:
                    rel_x, rel_y = 0, 0

                timestamp = time.time() - self.start_time
                action = {
                    "time": round(timestamp, 3),
                    "type": "mouse_click",
                    "button": event.button,
                    "event_type": event.event_type,  # down / up
                    "x": rel_x,
                    "y": rel_y,
                    "capture_rect": list(self.capture_rect) if self.capture_rect else None
                }
                self.actions.append(action)

        try:
            self._mouse_listener = mouse.hook(on_mouse)
            self._mouse_listener_active = True
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"⚠️ Не удалось отследить мышь: {e}")

    def _stop_key_listener(self):
        """Остановка слушателя клавиш и мыши"""
        try:
            if self._key_listener:
                keyboard.unhook(self._key_listener)
                self._key_listener = None
            self._key_listener_active = False
        except:
            pass

        try:
            if hasattr(self, '_mouse_listener') and self._mouse_listener:
                mouse.unhook(self._mouse_listener)
                self._mouse_listener = None
            self._mouse_listener_active = False
        except:
            pass

        self._mouse_move_active = False


    # -----------------------------
    # Сохранение данных
    # -----------------------------
    def _flush_frame_buffer(self):
        """Сохранить все кадры из буфера на диск"""
        with self._buffer_lock:
            for frame_name, img_bytes in self._frame_buffer:
                frame_path = os.path.join(self.frames_dir, frame_name)
                with open(frame_path, "wb") as f:
                    f.write(img_bytes)
            count = len(self._frame_buffer)
            self._frame_buffer.clear()

        if self.status_callback:
            self.status_callback(f"💾 Сохранено {count} кадров на диск")
    def _save_actions(self):
        """Сохранить actions.json"""
        data = {
            "session": self.session_dir,
            "start_time": datetime.now().isoformat(),
            "fps": self.fps,
            "window_rect": list(self.game_window_rect),
            "capture_rect": list(self.capture_rect),  # Сохраняем capture_rect для правильной конвертации координат
            "total_frames": len(self._frame_buffer) + len([f for f in os.listdir(self.frames_dir) if f.endswith('.jpg')]) if os.path.exists(self.frames_dir) else len(self._frame_buffer),
            "actions": self.actions
        }

        actions_path = os.path.join(self.session_dir, "actions.json")
        with open(actions_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # -----------------------------
    # Утилиты
    # -----------------------------
    @staticmethod
    def _get_next_session_num(output_dir):
        """Получить следующий номер сессии"""
        if not os.path.exists(output_dir):
            return 1

        sessions = [d for d in os.listdir(output_dir) if d.startswith("session_")]
        if not sessions:
            return 1

        nums = []
        for s in sessions:
            try:
                num = int(s.split("_")[1])
                nums.append(num)
            except:
                pass

        return max(nums) + 1 if nums else 1
