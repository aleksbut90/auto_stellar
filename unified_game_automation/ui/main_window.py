# Main tabbed window for the Unified Game Automation Tool
# Title: "Автоматизация Звездной Россыпи и Крыльев Силы"

import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import mouse
from core.game_connector import GameConnector
from core.ocr_engine import OCREngine
from core.emergency_stop import install_emergency_hook, remove_emergency_hook, set_stop_flag
# ОТКЛЮЧЕНО: from ui.arrival_tab import ArrivalTab
# ОТКЛЮЧЕНО: from ui.collection_tab import CollectionTab
# ОТКЛЮЧЕНО: from ui.heils_clicker_tab import HeilsClickerTab
from ui.stellar_tab import StellarTab
from ui.avtobot_tab import AvtobotTab
from ui.scenario_editor_tab import ScenarioEditorTab
from ui.help_tab import HelpTab

class MainWindow:
    def __init__(self):
        """Инициализация главного окна с вкладками"""
        self.root = tk.Tk()
        self.root.title("Автоматизация Звёздной Россыпи")
        self.root.geometry("650x900")
        self.root.attributes("-topmost", True)
        
        # Цветовая схема
        self.colors = {
            "bg": "#F5F5F5",
            "accent": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "danger": "#F44336",
            "text": "#212121",
            "text_secondary": "#757575"
        }

        # Настройка масштабируемости шрифтов (увеличенные)
        self.default_font = ("Segoe UI", 12)
        self.heading_font = ("Segoe UI", 13, "bold")
        self.title_font = ("Segoe UI", 14, "bold")

        # Отслеживание текущего запущенного инструмента (взаимное исключение)
        self.current_running_tool = None

        # Инициализация переменной статуса
        self.status_var = tk.StringVar(value="Готово к работе")

        # Общие компоненты (после создания status_var)
        self.game_connector = GameConnector(self.update_status)
        self.ocr_engine = OCREngine(self.update_status)

        # Настройка аварийной остановки (клавиша ESC) - ДВА уровня защиты
        self.keyboard_enabled = False
        
        # Уровень 1: Низкоуровневый хук Windows API (работает даже с pydirectinput)
        try:
            if install_emergency_hook(self.emergency_stop):
                self.keyboard_enabled = True
                print("✅ ESC хук уровня Windows API установлен")
        except Exception as e:
            print(f"⚠️ Не удалось установить низкоуровневый хук ESC: {e}")
        
        # Уровень 2: Стандартный хук keyboard (для резерва)
        try:
            keyboard.add_hotkey('esc', self.emergency_stop)
            self.keyboard_enabled = True
            print("✅ Стандартный хук ESC установлен")
        except Exception as e:
            print(f"⚠️ Не удалось настроить горячую клавишу ESC (запустите от администратора): {e}")

        # Настройка стилей
        self.configure_styles()

        # Установка иконки окна
        self.set_window_icon()

        # Создание UI
        self.create_ui()

        # Настройка обработчика закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_window_icon(self):
        """Установка иконки окна"""
        try:
            import os
            # Иконка рядом с main.py
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
                self.icon = icon  # Сохраняем ссылку чтобы GC не удалил
        except Exception as e:
            pass  # Если иконка не загрузилась - не страшно

    def configure_styles(self):
        """Настройка современных стилей для виджетов"""
        try:
            style = ttk.Style()
            style.theme_use('vista')  # Более стабильная тема для Windows
        except:
            pass  # Если тема не доступна, используем стандартную

    def create_ui(self):
        """Создание главного UI с вкладками"""
        # Главный фрейм с увеличенными отступами
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(style='TFrame')

        # Авто-подключение к игре и отображение статуса подключения
        self.auto_connect_to_game()

        # Панель статуса (сверху)
        status_bar = ttk.Frame(main_frame)
        status_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Индикатор статуса
        self.status_icon = ttk.Label(status_bar, text="●", 
                                    foreground=self.colors['success'],
                                    font=("Segoe UI", 14))
        self.status_icon.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(status_bar, textvariable=self.status_var,
                                     style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=(8, 0))

        # Аварийная остановка - выделена цветом
        emergency_frame = ttk.Frame(main_frame)
        emergency_frame.pack(fill=tk.X, pady=(0, 15))
        emergency_frame.configure(style='TFrame')
        
        emergency_bg = ttk.Frame(emergency_frame, relief=tk.FLAT)
        emergency_bg.pack(fill=tk.X)
        
        # Красная полоска слева для привлечения внимания
        warning_strip = tk.Frame(emergency_bg, bg=self.colors['danger'], width=4)
        warning_strip.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        emergency_label = ttk.Label(emergency_bg, text="🚨 Аварийная остановка: ESC",
                                   style='Emergency.TLabel')
        emergency_label.pack(side=tk.LEFT, pady=8)

        # Универсальные кнопки Старт/Стоп
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Контейнер для кнопок с выравниванием по центру
        buttons_container = ttk.Frame(control_frame)
        buttons_container.pack(fill=tk.X)

        self.btn_start = ttk.Button(buttons_container, text="▶  Старт", 
                                   command=self.unified_start, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_stop = ttk.Button(buttons_container, text="⏹  Стоп", 
                                  command=self.unified_stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

        # Создание книги вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Привязка события смены вкладки для остановки автоматизации при переключении
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Создание фреймов для вкладок
        stellar_frame = ttk.Frame(self.notebook)
        avtobot_frame = ttk.Frame(self.notebook)
        scenario_frame = ttk.Frame(self.notebook)
        help_frame = ttk.Frame(self.notebook)

        # Добавление вкладок в книгу
        self.notebook.add(stellar_frame, text="⭐ Звёздная Россыпь")
        self.notebook.add(avtobot_frame, text="🤖 Автобот")
        self.notebook.add(scenario_frame, text="🎮 Редактор сценариев")
        self.notebook.add(help_frame, text="❓ Помощь")

        # Создание вкладок
        self.stellar_tab = StellarTab(stellar_frame, self)
        self.avtobot_tab = AvtobotTab(avtobot_frame, self)
        self.scenario_editor_tab = ScenarioEditorTab(scenario_frame, self)
        self.help_tab = HelpTab(help_frame, self)

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
                self.stellar_tab,
                self.avtobot_tab,
                self.scenario_editor_tab,
                self.help_tab
            ]
            if 0 <= selected_index < len(tabs):
                return tabs[selected_index]
        except (AttributeError, tk.TclError):
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
        """Универсальный метод остановки"""
        if not self.current_running_tool:
            return

        if self.current_running_tool == "Звездная Россыпь":
            self.stellar_tab.stop_automation()
        elif self.current_running_tool == "Автобот":
            self.avtobot_tab.emergency_stop()
        elif self.current_running_tool == "Игровой бот":
            self.game_bot_tab.stop_bot()

        self.clear_running_tool()

    def emergency_stop(self):
        """Аварийная остановка по клавише ESC"""
        # Создаём файл-флаг для бота (работает даже когда бот контролирует ввод)
        set_stop_flag()
        
        # Немедленно очищаем все очереди ввода
        try:
            import ctypes
            ctypes.windll.user32.FlushInput()
        except:
            pass

        if self.current_running_tool:
            self.update_status(f"🚨 АВАРИЙНАЯ ОСТАНОВКА - {self.current_running_tool} остановлен!")

            if self.current_running_tool == "Звездная Россыпь":
                self.stellar_tab.emergency_stop()
            elif self.current_running_tool == "Автобот":
                self.avtobot_tab.emergency_stop()
            elif self.current_running_tool == "Игровой бот":
                self.game_bot_tab.stop_bot()

            self.clear_running_tool()

            # Поднимаем окно наверх и мигаем им
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.update()
            self.root.attributes('-topmost', False)
            
            # Звуковой сигнал (если доступен)
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except:
                pass

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
    
    def on_closing(self):
        """Очистка при закрытии приложения"""
        # Останавливаем бота если работает
        if hasattr(self, 'scenario_editor_tab') and self.scenario_editor_tab:
            try:
                self.scenario_editor_tab.stop_bot()
            except:
                pass
        
        # Удаляем хуки
        remove_emergency_hook()
        keyboard.unhook_all()
        self.root.destroy()

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
