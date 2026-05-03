"""
Scenario Engine v3.1 — детерминированный движок с логами триггеров и нормальным idle
"""

import os
import time
import cv2
import numpy as np
from PIL import ImageGrab
import pydirectinput
import threading


class ScenarioEngine:
    def __init__(self, capture_rect=None, startup_idle_delay=5.0):
        if capture_rect is None:
            import win32api
            self.capture_rect = [
                0,
                0,
                win32api.GetSystemMetrics(0),
                win32api.GetSystemMetrics(1)
            ]
        else:
            self.capture_rect = capture_rect

        self.running = False
        self.status_callback = None

        self.scenarios = []
        self.idle_actions = []
        self.idle_delay = 2.0
        self.startup_idle_delay = startup_idle_delay
        self._startup_idle_done = False

        # Потокобезопасное состояние
        self.lock = threading.Lock()
        self.active_scenario = None          # текущий выполняемый сценарий
        self.wake_event = threading.Event()  # будит поток исполнения

        self._trigger_thread = None
        self._execution_thread = None

        # Результат последнего сработавшего триггера (для use_trigger_position)
        self.last_trigger_result = None

    # ==================== ПУБЛИЧНЫЙ API ====================

    def load_scenarios(self, scenarios_list):
        self.scenarios = scenarios_list or []
        return len(self.scenarios)

    def start(self, status_callback=None):
        self.running = True
        self.status_callback = status_callback
        self._startup_idle_done = False
        self.active_scenario = None
        self.wake_event.clear()
        self.last_trigger_result = None

        self._trigger_thread = threading.Thread(
            target=self._trigger_monitor,
            daemon=True,
            name="ScenarioTriggerMonitor"
        )
        self._execution_thread = threading.Thread(
            target=self._execution_loop,
            daemon=True,
            name="ScenarioExecutor"
        )
        self._trigger_thread.start()
        self._execution_thread.start()

        self._log("▶️  Движок сценариев запущен")

    def stop(self):
        self.running = False
        self.wake_event.set()
        self._log("⏹️  Движок сценариев остановлен")

    def _log(self, msg):
        if self.status_callback:
            try:
                self.status_callback(msg)
            except Exception:
                pass

    # ==================== ПОТОК 1: МОНИТОРИНГ ТРИГГЕРОВ ====================

    def _trigger_monitor(self):
        """Постоянно сканирует экран и ищет срабатывание триггеров"""
        while self.running:
            found_scenario = None
            found_result = None

            for scenario in self.scenarios:
                if not self.running:
                    return

                if not scenario.get('enabled', True):
                    continue

                # Если этот сценарий уже активен и он цикличный — не перебиваем сам себя
                with self.lock:
                    if self.active_scenario is scenario and scenario.get('repeat', False):
                        continue

                trigger = scenario.get('trigger', {})
                res = self._check_trigger(trigger)

                # Временный лог можно оставить — очень помогает при отладке
                # self._log(f"🔎 '{scenario.get('name','?')}', found={res.get('found')}, best={res.get('best_match', None)}")

                if res.get('found'):
                    found_scenario = scenario
                    found_result = res
                    break

            if found_scenario:
                with self.lock:
                    self.active_scenario = found_scenario
                    self.last_trigger_result = found_result
                    self.wake_event.set()
                    self._log(
                        f"🎯 Триггер сработал: '{found_scenario.get('name', '?')}', "
                        f"conf={found_result.get('confidence', found_result.get('best_match', 0)):.2f}"
                    )

            time.sleep(0.2)

    # ==================== ПОТОК 2: ИСПОЛНЕНИЕ СЦЕНАРИЕВ / IDLE ====================

    def _execution_loop(self):
        """Основной цикл исполнения: либо сценарий, либо idle"""
        while self.running:
            with self.lock:
                current = self.active_scenario

            if current:
                self._run_scenario_actions(current)
            else:
                # Первый запуск — можно подождать перед idle
                if not self._startup_idle_done:
                    self._log(f"⏳ Ожидание перед idle ({self.startup_idle_delay}с)...")
                    self.wake_event.wait(timeout=self.startup_idle_delay)
                    self.wake_event.clear()
                    self._startup_idle_done = True
                    continue

                # Idle-действия
                if self.idle_actions:
                    self._log("💤 Выполняю idle-действия")
                    self._run_idle_actions()

                # Ждём либо новый триггер, либо таймаут idle
                self.wake_event.wait(timeout=self.idle_delay)
                self.wake_event.clear()

    def _run_scenario_actions(self, scenario):
        is_repeat = scenario.get('repeat', False)
        name = scenario.get('name', 'unknown')

        if is_repeat:
            self._log(f"🔒 Цикличный сценарий: '{name}'")

        while self.running:
            # Проверка актуальности
            with self.lock:
                if self.active_scenario is not scenario:
                    return

            # Выполняем действия
            for action in scenario.get('actions', []):
                with self.lock:
                    if self.active_scenario is not scenario:
                        return
                self._execute_single(action)

            # Если НЕ repeat → выходим
            if not is_repeat:
                with self.lock:
                    if self.active_scenario is scenario:
                        self.active_scenario = None
                        self.wake_event.set()
                self._log(f"✅ '{name}' завершён (1 раз)")
                return

            # Если repeat=True → ждём и повторяем
            delay = scenario.get('delay', 1.0)
            if self.wake_event.wait(timeout=delay):
                self.wake_event.clear()

    def _run_idle_actions(self):
        """Выполняет idle-действия. Прерывается, если появился активный сценарий."""
        for action in self.idle_actions:
            with self.lock:
                if self.active_scenario is not None:
                    return
            self._execute_single(action)

    # ==================== ВЫПОЛНЕНИЕ ОДНОГО ДЕЙСТВИЯ ====================

    def _execute_single(self, action):
        """Атомарное выполнение одного действия"""
        if not self.running:
            return

        at = action.get('type')

        try:
            if at == 'mouse_move':
                x = action.get('x', 0.5)
                y = action.get('y', 0.5)

                # Поддержка use_trigger_position
                if action.get('use_trigger_position') and self.last_trigger_result:
                    cx = self.last_trigger_result.get('screen_x', None)
                    cy = self.last_trigger_result.get('screen_y', None)
                    if cx is not None and cy is not None:
                        sx, sy = cx, cy
                    else:
                        sx = self.capture_rect[0] + int(x * self.capture_rect[2])
                        sy = self.capture_rect[1] + int(y * self.capture_rect[3])
                else:
                    sx = self.capture_rect[0] + int(x * self.capture_rect[2])
                    sy = self.capture_rect[1] + int(y * self.capture_rect[3])

                pydirectinput.moveTo(sx, sy, duration=action.get('duration', 0))

            elif at == 'mouse_click':
                pydirectinput.click(button=action.get('button', 'left'))

            elif at == 'mouse_right_click':
                pydirectinput.click(button='right')

            elif at == 'mouse_down':
                pydirectinput.mouseDown(button=action.get('button', 'left'))

            elif at == 'mouse_up':
                pydirectinput.mouseUp(button=action.get('button', 'left'))

            elif at == 'key_press':
                pydirectinput.press(action.get('key', ''))

            elif at == 'key_down':
                pydirectinput.keyDown(action.get('key', ''))

            elif at == 'key_up':
                pydirectinput.keyUp(action.get('key', ''))

            elif at == 'key_combo':
                keys = action.get('keys', [])
                if len(keys) > 1:
                    for k in keys[:-1]:
                        pydirectinput.keyDown(k)
                    pydirectinput.press(keys[-1])
                    for k in reversed(keys[:-1]):
                        pydirectinput.keyUp(k)
                elif keys:
                    pydirectinput.press(keys[0])

            elif at == 'wait':
                time.sleep(action.get('duration', 0.5))

        except Exception as e:
            self._log(f"⚠️  Ошибка действия '{at}': {e}")

    # ==================== ТРИГГЕРЫ ====================

    def _check_trigger(self, trigger):
        t = trigger.get('type', 'template')
        if t == 'template':
            return self._check_template_trigger(trigger)
        elif t == 'pixel_color':
            return self._check_color_trigger(trigger)
        else:
            return {'found': False}

    def _check_template_trigger(self, trigger):
        templates = trigger.get('templates') or trigger.get('template')
        threshold = trigger.get('threshold', 0.70)
        area = trigger.get('search_area', [0, 0, 0, 0])

        if isinstance(templates, str):
            templates = [templates]
        if not templates:
            return {'found': False, 'best_match': 0.0}

        screen = self._capture_screen()
        if screen is None or screen.size == 0:
            return {'found': False, 'best_match': 0.0}

        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        ox, oy = 0, 0
        if area and sum(area) > 0:
            x, y, w, h = area
            # защита от выхода за границы
            h = min(h, gray.shape[0] - y)
            w = min(w, gray.shape[1] - x)
            if w <= 0 or h <= 0:
                return {'found': False, 'best_match': 0.0}
            gray = gray[y:y + h, x:x + w]
            ox, oy = x, y

        best_val, best_loc, best_wh = 0.0, None, None

        for path in templates:
            try:
                if not path or not os.path.exists(path):
                    continue
                data = np.fromfile(path, np.uint8)
                tpl = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
                if tpl is None:
                    continue

                th, tw = tpl.shape
                if th > gray.shape[0] or tw > gray.shape[1]:
                    continue

                res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)

                if max_val > best_val:
                    best_val, best_loc, best_wh = max_val, max_loc, (tw, th)
            except Exception:
                continue

        if best_val >= threshold and best_loc and best_wh:
            tw, th = best_wh
            cx = best_loc[0] + tw // 2 + ox
            cy = best_loc[1] + th // 2 + oy

            nx = max(0.0, min(1.0, (cx - self.capture_rect[0]) / self.capture_rect[2]))
            ny = max(0.0, min(1.0, (cy - self.capture_rect[1]) / self.capture_rect[3]))

            return {
                'found': True,
                'screen_x': cx,
                'screen_y': cy,
                'norm_x': nx,
                'norm_y': ny,
                'confidence': best_val
            }

        return {'found': False, 'best_match': float(best_val)}

    def _check_color_trigger(self, trigger):
        x = trigger.get('x', 0)
        y = trigger.get('y', 0)
        tolerance = trigger.get('tolerance', 30)

        screen = self._capture_screen()
        if screen is None or screen.size == 0:
            return {'found': False}

        if y < 0 or y >= screen.shape[0] or x < 0 or x >= screen.shape[1]:
            return {'found': False}

        px = screen[y, x]
        cmap = {
            'red':   [0, 0, 255],
            'green': [0, 255, 0],
            'blue':  [255, 0, 0],
            'white': [255, 255, 255],
            'black': [0, 0, 0]
        }
        exp = cmap.get(trigger.get('color', 'white'), [255, 255, 255])
        dist = np.sqrt(sum((int(px[i]) - int(exp[i])) ** 2 for i in range(3)))

        return {'found': dist < tolerance, 'actual': px.tolist(), 'distance': float(dist)}

    # ==================== ЗАХВАТ ЭКРАНА ====================

    def _capture_screen(self):
        x, y, w, h = self.capture_rect
        try:
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h)).convert("RGB")
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception:
            return None


if __name__ == "__main__":
    print("Scenario Engine v3.1 — готов к интеграции")
