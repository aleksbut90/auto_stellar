"""
Вкладка Автобот - запись датасета для обучения
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from automation.bot_recorder import BotRecorder


class AvtobotTab:
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window

        self.recorder = BotRecorder(main_window.update_status)
        self.game_window_coords = None

        self.create_ui()

    def create_ui(self):
        """Создание UI вкладки Автобот"""
        main_frame = ttk.Frame(self.parent_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ====== СЕКЦИЯ 1: ОКНО ИГРЫ ======
        window_section = ttk.LabelFrame(main_frame, text="🎮 Окно игры", padding="15")
        window_section.pack(fill=tk.X, pady=(0, 15))

        window_info_frame = ttk.Frame(window_section)
        window_info_frame.pack(fill=tk.X)

        self.window_coord_var = tk.StringVar(value="Не определено")
        ttk.Label(window_info_frame, textvariable=self.window_coord_var,
                 font=self.main_window.default_font).pack(side=tk.LEFT)

        ttk.Button(window_info_frame, text="📍 Выбрать окно игры",
                  command=self.capture_game_window).pack(side=tk.RIGHT)

        # ====== СЕКЦИЯ 2: ЗАПИСЬ ДАТАСЕТА ======
        record_section = ttk.LabelFrame(main_frame, text="📹 Запись датасета", padding="15")
        record_section.pack(fill=tk.X, pady=(0, 15))

        # Статус записи
        status_frame = ttk.Frame(record_section)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.record_status_var = tk.StringVar(value="⚪ Не записывается")
        self.record_status_label = ttk.Label(status_frame, textvariable=self.record_status_var,
                                            font=self.main_window.heading_font)
        self.record_status_label.pack(side=tk.LEFT)

        # Счётчик кадров
        self.frame_count_var = tk.StringVar(value="Кадров: 0")
        ttk.Label(status_frame, textvariable=self.frame_count_var,
                 font=self.main_window.default_font,
                 foreground=self.main_window.colors['text_secondary']).pack(side=tk.LEFT, padx=(15, 0))

        # Кнопки управления записью
        buttons_frame = ttk.Frame(record_section)
        buttons_frame.pack(fill=tk.X)

        self.btn_start_record = ttk.Button(buttons_frame, text="🔴 Начать запись",
                                           command=self.start_recording)
        self.btn_start_record.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_stop_record = ttk.Button(buttons_frame, text="⏹ Остановить",
                                          command=self.stop_recording, state=tk.DISABLED)
        self.btn_stop_record.pack(side=tk.LEFT)

        # Подсказка
        hint = ttk.Label(record_section,
                        text="💡 Записывает скриншоты (JPEG 1280×720) + нажатия клавиш и мышь (10 FPS)",
                        foreground=self.main_window.colors['text_secondary'],
                        font=self.main_window.default_font)
        hint.pack(fill=tk.X, pady=(10, 0))

        # ====== СЕКЦИЯ 3: ИНФОРМАЦИЯ О ДАТАСЕТЕ ======
        dataset_section = ttk.LabelFrame(main_frame, text="📂 Информация о датасете", padding="15")
        dataset_section.pack(fill=tk.X, pady=(0, 15))

        dataset_text = ("Формат датасета:\n"
                       "  dataset/\n"
                       "    session_001/\n"
                       "      frames/  — скриншоты JPEG 1280×720 (frame_00001.jpg, ...)\n"
                       "      actions.json — клавиши + мышь с таймстампами\n\n"
                       "Для обучения модели собери 5-10 записей прохождения данжа.\n"
                       "1 минута записи ≈ 150-300 МБ")
        ttk.Label(dataset_section, text=dataset_text, wraplength=550,
                 font=self.main_window.default_font).pack(anchor=tk.W)

        # Начать обновление статуса записи
        self._update_frame_count()

    def capture_game_window(self):
        """Захват координат окна игры"""
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                self.main_window.update_status("Игра не найдена")
                return

        rect = self.main_window.game_connector.get_window_rect()
        if rect:
            self.game_window_coords = (rect.left, rect.top, rect.width(), rect.height())
            self.recorder.set_game_window_rect(self.game_window_coords)
            self.window_coord_var.set(
                f"✓ {self.game_window_coords[0]}, {self.game_window_coords[1]} "
                f"({self.game_window_coords[2]}x{self.game_window_coords[3]})"
            )
            self.main_window.update_status("Окно игры определено")
            self.main_window.update_unified_buttons()
        else:
            self.main_window.update_status("Не удалось получить координаты окна")

    def start_recording(self):
        """Начать запись датасета"""
        if not self.game_window_coords:
            messagebox.showwarning("Окно не выбрано", "Сначала выбери окно игры")
            return

        if not self.main_window.set_running_tool("Автобот"):
            return

        # Убираем topmost главного окна чтобы оно не было поверх игры
        self._was_topmost = self.main_window.root.attributes("-topmost")
        self.main_window.root.attributes("-topmost", False)

        # Передаём HWND главного окна для отправки на задний план
        main_hwnd = self.main_window.root.winfo_id()
        started = self.recorder.start(main_window_hwnd=main_hwnd)
        if started:
            self.record_status_var.set("🔴 Запись...")
            self.record_status_label.configure(foreground=self.main_window.colors['danger'])
            self.btn_start_record.configure(state=tk.DISABLED)
            self.btn_stop_record.configure(state=tk.NORMAL)

    def stop_recording(self):
        """Остановить запись"""
        self.recorder.stop()
        self.record_status_var.set("⚪ Запись остановлена")
        self.record_status_label.configure(foreground=self.main_window.colors['text_secondary'])
        self.btn_start_record.configure(state=tk.NORMAL)
        self.btn_stop_record.configure(state=tk.DISABLED)

        # Возвращаем topmost главного окна
        if hasattr(self, '_was_topmost') and self._was_topmost:
            self.main_window.root.attributes("-topmost", True)

        self.main_window.clear_running_tool()

    def can_start(self):
        """Можно ли начать запись"""
        return self.game_window_coords is not None

    def emergency_stop(self):
        """Аварийная остановка"""
        if self.recorder.is_recording():
            self.recorder.stop()
            self.record_status_var.set("⚪ Аварийная остановка")
            self.btn_start_record.configure(state=tk.NORMAL)
            self.btn_stop_record.configure(state=tk.DISABLED)
            self.main_window.clear_running_tool()

    def _update_frame_count(self):
        """Обновление счётчика кадров"""
        if self.recorder.is_recording():
            # Считаем кадры в буфере (RAM) + уже на диске
            ram_frames = len(self.recorder._frame_buffer) if hasattr(self.recorder, '_frame_buffer') else 0
            disk_frames = 0
            if self.recorder.frames_dir and os.path.exists(self.recorder.frames_dir):
                disk_frames = len([f for f in os.listdir(self.recorder.frames_dir) if f.endswith('.jpg')])
            self.frame_count_var.set(f"Кадров: {ram_frames + disk_frames} (RAM: {ram_frames})")

        # Повторить через 1 секунду
        self.parent_frame.after(1000, self._update_frame_count)
