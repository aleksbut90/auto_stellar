import tkinter as tk
from tkinter import ttk
from automation.heils_clicker import HeilsClickerAutomation
from core.settings_manager import SettingsManager


class HeilsClickerTab:
    """Простой непрерывный кликер, который кликает в определенной точке до остановки."""

    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Менеджер настроек для сохранения (используя unified settings.json)
        self.settings = SettingsManager(tab_section="heils_clicker")

        self.automation = HeilsClickerAutomation(
            main_window.game_connector,
            main_window.update_status
        )

        # Состояние UI
        self.click_coords = None
        self.click_coord_var = tk.StringVar(value="Не установлена")
        self.delay_var = tk.IntVar(value=200)  # мс

        self.create_ui()
        
        # Загрузка сохраненных настроек
        self.load_saved_settings()

    def create_ui(self):
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм контента, который может сжиматься (все кроме кнопок)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Секция координат
        coords_frame = ttk.LabelFrame(content_frame, text="Цель клика", padding="10")
        coords_frame.pack(fill=tk.X, pady=(0, 10))

        coord_row = ttk.Frame(coords_frame)
        coord_row.pack(fill=tk.X, pady=2)

        ttk.Label(coord_row, text="Позиция:").pack(side=tk.LEFT)
        ttk.Label(coord_row, textvariable=self.click_coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(coord_row, text="Установить позицию клика", command=self.set_click_position).pack(side=tk.RIGHT)

        # Секция задержки
        delay_frame = ttk.LabelFrame(content_frame, text="Задержка между кликами (мс)", padding="10")
        delay_frame.pack(fill=tk.X, pady=(0, 10))

        delay_row = ttk.Frame(delay_frame)
        delay_row.pack(fill=tk.X, pady=2)

        delay_spin = ttk.Spinbox(
            delay_row,
            from_=0,
            to=10000,
            increment=50,
            textvariable=self.delay_var,
            width=8,
            command=self.update_delay
        )
        delay_spin.pack(side=tk.LEFT)
        self.delay_var.trace_add("write", lambda *_: self.update_delay())

    def set_click_position(self):
        """Захват позиции клика из окна игры."""
        def on_success(rel_x, rel_y):
            self.click_coords = (rel_x, rel_y)
            self.automation.set_click_position(self.click_coords)
            self.click_coord_var.set(f"({rel_x}, {rel_y})")
            self.main_window.update_status(f"Позиция клика установлена на ({rel_x}, {rel_y})")
            # Сохранение в настройки
            self.settings.set_button("click_position", (rel_x, rel_y))
            self.main_window.update_unified_buttons()

        self.main_window.capture_button_coordinates(
            "Цель клика",
            "Кликните по точке в игре, где Heils Кликер должен кликать неоднократно.",
            on_success
        )

    def update_delay(self):
        """Обновление задержки в автоматизации при изменении значения."""
        try:
            val = int(str(self.delay_var.get() or "0"))
        except Exception:
            val = 0
        self.automation.set_delay_ms(val)
        # Сохранение в настройки
        self.settings.set_delay_ms(val)
    
    def load_saved_settings(self):
        """Загрузка сохраненных настроек из файла"""
        # Загрузка позиции клика
        click_pos = self.settings.get_button("click_position")
        if click_pos:
            self.click_coords = click_pos
            self.automation.set_click_position(self.click_coords)
            self.click_coord_var.set(f"({click_pos[0]}, {click_pos[1]})")
            # Не вызывать update_unified_buttons здесь - вызывается после инициализации всех вкладок
        
        # Загрузка задержки
        delay_ms = self.settings.get_delay_ms()
        if delay_ms:
            self.delay_var.set(delay_ms)
            self.automation.set_delay_ms(delay_ms)

    def can_start(self):
        """Проверка возможности запуска автоматизации (позиция клика установлена)"""
        return self.click_coords is not None
    
    def start_clicking(self):
        """Запуск цикла кликов."""
        if not self.main_window.set_running_tool("Heils Кликер"):
            return

        self.update_delay()
        started = self.automation.start()
        if not started:
            self.main_window.clear_running_tool()

    def stop_clicking(self):
        """Остановка цикла кликов."""
        self.automation.stop()
        self.main_window.clear_running_tool()
        self.main_window.update_status("Heils Кликер остановлен")

    def emergency_stop(self):
        """Аварийная остановка."""
        self.automation.emergency_stop()
        self.main_window.clear_running_tool()

