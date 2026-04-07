# Main tabbed window for the Unified Game Automation Tool
# Title: "Автоматизация Звездной Россыпи и Крыльев Силы"

import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import mouse
from core.game_connector import GameConnector
from core.ocr_engine import OCREngine
from ui.stellar_tab import StellarTab
from ui.arrival_tab import ArrivalTab
from ui.collection_tab import CollectionTab
from ui.heils_clicker_tab import HeilsClickerTab
from ui.troubleshooting_tab import TroubleshootingTab
from ui.help_tab import HelpTab

class MainWindow:
    def __init__(self):
        """Инициализация главного окна с вкладками"""
        self.root = tk.Tk()
        self.root.title("Автоматизация Звездной Россыпи и Крыльев Силы")
        self.root.geometry("800x900")
        self.root.attributes("-topmost", True)
        
        # Настройка масштабируемости шрифтов
        self.default_font = ("Arial", 10)
        self.heading_font = ("Arial", 11, "bold")

        # Отслеживание текущего запущенного инструмента (взаимное исключение)
        self.current_running_tool = None

        # Инициализация переменной статуса
        self.status_var = tk.StringVar(value="Инициализация...")

        # Общие компоненты (после создания status_var)
        self.game_connector = GameConnector(self.update_status)
        self.ocr_engine = OCREngine(self.update_status)

        # Настройка аварийной остановки (клавиша ESC)
        keyboard.add_hotkey('esc', self.emergency_stop)

        # Создание UI
        self.create_ui()

        # Настройка обработчика закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        """Создание главного UI с вкладками"""
        # Главный фрейм с увеличенными отступами
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Авто-подключение к игре и отображение статуса
        self.auto_connect_to_game()

        # Информация об аварийной остановке - размещена сверху для лучшей видимости
        emergency_frame = ttk.Frame(main_frame)
        emergency_frame.pack(fill=tk.X, pady=(0, 15))
        emergency_label = ttk.Label(emergency_frame, text="Аварийная остановка: ESC",
                                   foreground="red", font=self.heading_font)
        emergency_label.pack(anchor=tk.W)

        # Универсальные кнопки Старт/Стоп
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.btn_start = ttk.Button(control_frame, text="Старт", command=self.unified_start, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_stop = ttk.Button(control_frame, text="Стоп", command=self.unified_stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

        # Создание книги вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Привязка события смены вкладки для остановки автоматизации при переключении
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Создание фреймов для вкладок
        arrival_frame = ttk.Frame(self.notebook)
        stellar_frame = ttk.Frame(self.notebook)
        collection_frame = ttk.Frame(self.notebook)
        heils_frame = ttk.Frame(self.notebook)
        troubleshooting_frame = ttk.Frame(self.notebook)
        help_frame = ttk.Frame(self.notebook)

        # Добавление вкладок в книгу (Крылья Силы первыми)
        self.notebook.add(arrival_frame, text="Крылья Силы")
        self.notebook.add(stellar_frame, text="Звездная Россыпь")
        self.notebook.add(collection_frame, text="Заполнитель Коллекции")
        self.notebook.add(heils_frame, text="Heils Кликер")
        self.notebook.add(help_frame, text="Помощь")
        self.notebook.add(troubleshooting_frame, text="Решение Проблем")

        # Create tab instances
        self.arrival_tab = ArrivalTab(arrival_frame, self)
        self.stellar_tab = StellarTab(stellar_frame, self)
        self.collection_tab = CollectionTab(collection_frame, self)
        self.heils_clicker_tab = HeilsClickerTab(heils_frame, self)
        self.help_tab = HelpTab(help_frame, self)
        self.troubleshooting_tab = TroubleshootingTab(troubleshooting_frame, self)
        
        # Update unified buttons after all tabs are loaded
        self.update_unified_buttons()

    def auto_connect_to_game(self):
        """Автоматическое подключение к игре и отображение статуса подключения"""
        if self.game_connector.connect_to_game():
            # Получение информации об окне игры для отображения
            window_rect = self.game_connector.get_window_rect()
            if window_rect:
                window_info = f"Подключено к окну игры ({window_rect.width}x{window_rect.height})"
            else:
                window_info = "Подключено к окну игры"
            self.update_status(window_info)
        else:
            self.update_status("Игра не найдена")

    def update_status(self, message):
        """Обновление отображения статуса"""
        self.status_var.set(message)

    def set_running_tool(self, tool_name):
        """Установка текущего запущенного инструмента (взаимное исключение)"""
        if self.current_running_tool is not None and self.current_running_tool != tool_name:
            self.update_status(f"Невозможно запустить {tool_name}: {self.current_running_tool} уже запущен")
            return False

        self.current_running_tool = tool_name
        self.update_unified_buttons()
        return True

    def clear_running_tool(self):
        """Очистка текущего запущенного инструмента"""
        self.current_running_tool = None
        self.update_unified_buttons()
    
    def update_unified_buttons(self):
        """Обновление универсальных кнопок Старт/Стоп на основе текущего состояния"""
        if self.current_running_tool:
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            # Проверка возможности запуска текущей вкладки
            current_tab = self.get_current_tab()
            if current_tab and hasattr(current_tab, 'can_start'):
                can_start = current_tab.can_start()
            else:
                # Вкладка решения проблем или другие вкладки без автоматизации
                can_start = False
            
            self.btn_start.config(state=tk.NORMAL if can_start else tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
    
    def get_current_tab(self):
        """Получение экземпляра текущей выбранной вкладки"""
        try:
            selected_index = self.notebook.index(self.notebook.select())
            tabs = [
                self.arrival_tab,
                self.stellar_tab,
                self.collection_tab,
                self.heils_clicker_tab,
                self.help_tab,
                self.troubleshooting_tab
            ]
            if 0 <= selected_index < len(tabs):
                return tabs[selected_index]
        except (AttributeError, tk.TclError):
            # Вкладки еще не полностью инициализированы или книга не готова
            pass
        return None
    
    def on_tab_changed(self, event=None):
        """Обработка смены вкладки - остановка автоматизации при переключении"""
        if self.current_running_tool:
            self.unified_stop()
        
        # Обновление состояния кнопок для новой вкладки
        self.update_unified_buttons()
    
    def unified_start(self):
        """Универсальный метод запуска - запускает автоматизацию для текущей вкладки"""
        current_tab = self.get_current_tab()
        if not current_tab:
            return
        
        # Остановка любой запущенной автоматизации сначала
        if self.current_running_tool:
            self.unified_stop()
        
        # Запуск автоматизации текущей вкладки
        if hasattr(current_tab, 'start_automation'):
            current_tab.start_automation()
        elif hasattr(current_tab, 'start_clicking'):
            current_tab.start_clicking()
        
        # Обновление кнопок после запуска
        self.update_unified_buttons()
    
    def unified_stop(self):
        """Универсальный метод остановки - останавливает любую запущенную автоматизацию"""
        if not self.current_running_tool:
            return
        
        # Остановка whichever инструмент запущен
        if self.current_running_tool == "Звездная Россыпь":
            self.stellar_tab.stop_automation()
        elif self.current_running_tool == "Крылья Силы":
            self.arrival_tab.stop_automation()
        elif self.current_running_tool == "Заполнитель Коллекции":
            self.collection_tab.stop_automation()
        elif self.current_running_tool == "Heils Кликер":
            self.heils_clicker_tab.stop_clicking()
        
        self.clear_running_tool()
    
    def capture_button_coordinates(self, button_name, instruction_text, success_callback):
        """
        Общий метод для захвата координат кнопок на всех вкладках.
        
        Args:
            button_name: Название кнопки (например, "Применить", "Изменить", "Запечатлеть")
            instruction_text: Текст инструкции для отображения в messagebox
            success_callback: Функция для вызова с (rel_x, rel_y) при успехе
        """
        # Подключение к игре при необходимости
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                self.update_status("Игра не найдена")
                return
        
        self.update_status(f"Нажмите кнопку {button_name}...")
        
        # Изменение курсора для индикации режима клика
        self.root.config(cursor="crosshair")
        
        def capture_click():
            """Захват координат клика мыши"""
            try:
                # Ожидание клика мыши
                mouse.wait(button='left')
                x, y = mouse.get_position()
                
                # Преобразование в относительные координаты окна
                rel_x, rel_y, success = self.game_connector.convert_to_window_coords(x, y)
                
                if success:
                    success_callback(rel_x, rel_y)
                    self.update_status(f"{button_name} установлена на ({rel_x}, {rel_y})")
                else:
                    self.update_status("Не удалось преобразовать координаты")
            
            except Exception as e:
                self.update_status(f"Ошибка: {str(e)}")
            finally:
                # Сброс курсора
                self.root.config(cursor="")
        
        # Запуск захвата в потоке
        threading.Thread(target=capture_click, daemon=True).start()
    
    def define_ocr_area(self, area_callback):
        """
        Общий метод для определения области OCR на всех вкладках.
        
        Args:
            area_callback: Функция для вызова с выбранной областью
        """
        # Использование общего селектора областей
        if not hasattr(self, 'area_selector'):
            from core.area_selector import AreaSelector
            self.area_selector = AreaSelector(self.root, area_callback)
        else:
            self.area_selector.callback = area_callback
        
        self.area_selector.select_area()
    
    def emergency_stop(self):
        """Аварийная остановка по клавише ESC"""
        if self.current_running_tool:
            self.update_status(f"🚨 АВАРИЙНАЯ ОСТАНОВКА - {self.current_running_tool} остановлен!")

            # Остановка whichever инструмент запущен
            if self.current_running_tool == "Звездная Россыпь":
                self.stellar_tab.emergency_stop()
            elif self.current_running_tool == "Крылья Силы":
                self.arrival_tab.emergency_stop()
            elif self.current_running_tool == "Заполнитель Коллекции":
                self.collection_tab.emergency_stop()
            elif self.current_running_tool == "Heils Кликер":
                self.heils_clicker_tab.emergency_stop()

            self.clear_running_tool()

            # Вывод окна на передний план
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)

    def on_closing(self):
        """Очистка при закрытии приложения"""
        keyboard.unhook_all()  # Удаление всех хуков клавиатуры
        self.root.destroy()

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
