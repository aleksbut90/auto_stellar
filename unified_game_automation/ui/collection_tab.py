# Collection tab UI - Simplified with Start/Stop buttons

import tkinter as tk
from tkinter import ttk
import threading
import mouse
from data.collection_data import get_collection_buttons
from automation.collection_automation import CollectionAutomation
from core.settings_manager import SettingsManager

class CollectionTab:
    def __init__(self, parent_frame, main_window):
        """Инициализация вкладки Заполнитель Коллекции"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Менеджер настроек для сохранения (используя unified settings.json)
        self.settings = SettingsManager(tab_section="collection")

        # Компоненты автоматизации
        self.automation = CollectionAutomation(
            main_window.game_connector,
            main_window.update_status
        )

        # Переменные состояния UI
        self.button_coord_vars = {}
        self.area_status_vars = {}
        
        # Создание UI
        self.create_ui()
        
        # Загрузка сохраненных настроек
        self.load_saved_settings()

    def create_ui(self):
        """Создание UI коллекции"""
        # Главный фрейм с отступами
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм контента, который может сжиматься (все кроме кнопок)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Секция статуса настройки
        status_frame = ttk.LabelFrame(content_frame, text="Статус настройки", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.setup_status_label = ttk.Label(status_frame, text="⚠ Настройка не завершена", 
                                           foreground="orange", font=("Arial", 10, "bold"))
        self.setup_status_label.pack()

        # Секция областей обнаружения
        area_frame = ttk.LabelFrame(content_frame, text="Области обнаружения", padding="5")
        area_frame.pack(fill=tk.X, pady=(0, 10))

        areas = [
            ("collection_tabs", "Вкладки коллекции"),
            ("dungeon_list", "Список подземелий"),
            ("collection_items", "Элементы коллекции")
        ]

        for area_key, area_name in areas:
            frame = ttk.Frame(area_frame)
            frame.pack(fill=tk.X, pady=1)
            
            ttk.Button(frame, text=f"Установить {area_name}", 
                      command=lambda k=area_key: self.define_area(k)).pack(side=tk.LEFT)
            
            status_label = ttk.Label(frame, text="❌", foreground="red")
            status_label.pack(side=tk.RIGHT)
            self.area_status_vars[area_key] = status_label

        # Секция координат кнопок
        button_frame = ttk.LabelFrame(content_frame, text="Координаты кнопок", padding="5")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        all_buttons = {**get_collection_buttons(), 
                      "page_2": "Страница 2", "page_3": "Страница 3", 
                      "page_4": "Страница 4", "arrow_right": "Стрелка вправо"}

        for button_key, button_name in all_buttons.items():
            frame = ttk.Frame(button_frame)
            frame.pack(fill=tk.X, pady=1)

            ttk.Label(frame, text=f"{button_name}:").pack(side=tk.LEFT)
            
            coord_var = tk.StringVar(value="Не установлена")
            self.button_coord_vars[button_key] = coord_var
            ttk.Label(frame, textvariable=coord_var, foreground="blue", 
                     font=("Arial", 8)).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(frame, text="Установить", 
                      command=lambda k=button_key, n=button_name: self.set_button_coordinate(k, n)).pack(side=tk.RIGHT)

        # Секция настроек задержки
        delay_frame = ttk.LabelFrame(content_frame, text="Настройки задержки", padding="5")
        delay_frame.pack(fill=tk.X, pady=(0, 10))
        
        delay_input_frame = ttk.Frame(delay_frame)
        delay_input_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(delay_input_frame, text="Задержка (миллисекунды):").pack(side=tk.LEFT)
        
        self.delay_var = tk.IntVar(value=1000)  # По умолчанию 1000мс (1 секунда)
        delay_spinbox = ttk.Spinbox(delay_input_frame, from_=0, to=10000, increment=100, 
                                   textvariable=self.delay_var, width=8,
                                   command=self.update_delay)
        delay_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        # Привязка к изменениям переменной для перехвата ручного ввода
        self.delay_var.trace('w', lambda *args: self.update_delay())

    def load_saved_settings(self):
        """Загрузка настроек из файла и обновление UI"""
        # Загрузка задержки (конвертация из старого формата множителя если нужно)
        delay_ms = self.settings.get_delay_ms()
        self.delay_var.set(delay_ms)
        self.automation.set_delay_ms(delay_ms)
        
        # Загрузка и применение областей
        areas = self.settings.get_all_areas()
        for area_name, coords in areas.items():
            if coords:
                if area_name == "collection_tabs":
                    self.automation.set_collection_tabs_area(coords)
                elif area_name == "dungeon_list":
                    self.automation.set_dungeon_list_area(coords)
                elif area_name == "collection_items":
                    self.automation.set_collection_items_area(coords)
                
                # Обновление статуса
                if area_name in self.area_status_vars:
                    self.area_status_vars[area_name].config(text="✓", foreground="green")
        
        # Загрузка и применение кнопок
        buttons = self.settings.get_all_buttons()
        for button_name, coords in buttons.items():
            if coords:
                # Установка в автоматизацию
                if button_name == "auto_refill":
                    self.automation.set_auto_refill_button(coords)
                elif button_name == "register":
                    self.automation.set_register_button(coords)
                elif button_name == "yes":
                    self.automation.set_yes_button(coords)
                elif button_name == "page_2":
                    self.automation.set_page_2_button(coords)
                elif button_name == "page_3":
                    self.automation.set_page_3_button(coords)
                elif button_name == "page_4":
                    self.automation.set_page_4_button(coords)
                elif button_name == "arrow_right":
                    self.automation.set_arrow_right_button(coords)
                
                # Обновление UI
                if button_name in self.button_coord_vars:
                    self.button_coord_vars[button_name].set(f"({coords[0]}, {coords[1]})")
        
        self.update_setup_status()

    def update_setup_status(self):
        """Обновление отображения статуса настройки"""
        if self.settings.is_setup_complete():
            self.setup_status_label.config(text="✓ Готово", foreground="green")
        else:
            self.setup_status_label.config(text="⚠ Настройка не завершена", foreground="orange")

    def define_area(self, area_name, callback=None):
        """Определение конкретной области"""
        def area_callback(area):
            """Обратный вызов при выборе области"""
            # Сохранение в настройки
            self.settings.set_area(area_name, area)
            
            # Установка в автоматизацию
            if area_name == "collection_tabs":
                self.automation.set_collection_tabs_area(area)
            elif area_name == "dungeon_list":
                self.automation.set_dungeon_list_area(area)
            elif area_name == "collection_items":
                self.automation.set_collection_items_area(area)
            
            # Обновление UI
            if area_name in self.area_status_vars:
                self.area_status_vars[area_name].config(text="✓", foreground="green")
            
            self.main_window.update_status(f"✓ Область {area_name.replace('_', ' ').title()} сохранена")
            self.update_setup_status()
            self.main_window.update_unified_buttons()
            
            if callback:
                callback()

        # Использование общего селектора областей из главного окна
        self.main_window.define_ocr_area(area_callback)

    def set_button_coordinate(self, button_key, button_name, callback=None):
        """Установка координат для кнопки действия"""
        # Подключение к игре если нужно
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                self.main_window.update_status("Игра не найдена")
                return

        self.main_window.update_status(f"Нажмите на кнопку '{button_name}'...")

        # Изменение курсора для индикации режима клика
        self.main_window.root.config(cursor="crosshair")

        def capture_click():
            """Захват координат клика мыши"""
            try:
                # Ожидание клика мыши
                mouse.wait(button='left')
                x, y = mouse.get_position()

                # Преобразование в координаты относительно окна
                rel_x, rel_y, success = self.main_window.game_connector.convert_to_window_coords(x, y)

                if success:
                    # Сохранение в настройки
                    self.settings.set_button(button_key, (rel_x, rel_y))
                    
                    # Установка координат в автоматизацию в зависимости от типа кнопки
                    if button_key == "auto_refill":
                        self.automation.set_auto_refill_button((rel_x, rel_y))
                    elif button_key == "register":
                        self.automation.set_register_button((rel_x, rel_y))
                    elif button_key == "yes":
                        self.automation.set_yes_button((rel_x, rel_y))
                    elif button_key == "page_2":
                        self.automation.set_page_2_button((rel_x, rel_y))
                    elif button_key == "page_3":
                        self.automation.set_page_3_button((rel_x, rel_y))
                    elif button_key == "page_4":
                        self.automation.set_page_4_button((rel_x, rel_y))
                    elif button_key == "arrow_right":
                        self.automation.set_arrow_right_button((rel_x, rel_y))
                    
                    # Обновление UI
                    if button_key in self.button_coord_vars:
                        self.button_coord_vars[button_key].set(f"({rel_x}, {rel_y})")
                    
                    self.main_window.update_status(f"✓ Кнопка {button_name} сохранена")
                    self.update_setup_status()
                    self.main_window.update_unified_buttons()
                    
                    # Вызов обратного вызова если предоставлен
                    if callback:
                        callback()
                else:
                    self.main_window.update_status("Не удалось преобразовать координаты")

            except Exception as e:
                self.main_window.update_status(f"Ошибка: {str(e)}")
            finally:
                # Сброс курсора
                self.main_window.root.config(cursor="")

        # Запуск захвата в потоке
        threading.Thread(target=capture_click, daemon=True).start()

    def update_delay(self):
        """Обновление задержки в автоматизации"""
        try:
            delay_ms = self.delay_var.get()
            self.automation.set_delay_ms(delay_ms)
            self.settings.set_delay_ms(delay_ms)
            self.main_window.update_status(f"Задержка: {delay_ms}мс")
        except Exception as e:
            pass

    def can_start(self):
        """Проверка возможности запуска автоматизации (все необходимые настройки настроены)"""
        return self.settings.is_setup_complete()
    
    def start_automation(self):
        """Запуск автоматизации коллекции"""
        # Проверка, запущен ли уже инструмент отслеживания главного окна
        if not self.main_window.set_running_tool("Заполнитель коллекции"):
            return

        # Запуск автоматизации
        if not self.automation.start():
            # Не удалось запустить, очистка инструмента выполнения
            self.main_window.clear_running_tool()

    def stop_automation(self):
        """Остановка автоматизации коллекции"""
        self.automation.stop()
        self.main_window.clear_running_tool()

    def emergency_stop(self):
        """Аварийная остановка автоматизации"""
        self.automation.stop()
        self.main_window.clear_running_tool()