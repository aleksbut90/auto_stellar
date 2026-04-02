# Troubleshooting tab UI - Решение проблем
# Provides troubleshooting information and common solutions

import tkinter as tk
from tkinter import ttk

class TroubleshootingTab:
    def __init__(self, parent_frame, main_window):
        """Инициализация вкладки Решение проблем"""
        self.parent_frame = parent_frame
        self.main_window = main_window
        
        # Создание UI
        self.create_ui()
    
    def create_ui(self):
        """Создание UI решения проблем"""
        # Главный фрейм с отступами
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание прокручиваемого фрейма
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Секция Запуск от имени администратора
        admin_frame = ttk.LabelFrame(scrollable_frame, text="Запуск от имени администратора", padding="10")
        admin_frame.pack(fill=tk.X, pady=(0, 10))
        
        admin_text = "Приложение должно быть запущено от имени администратора для корректной работы.\n" \
                     "Щелкните правой кнопкой мыши по исполняемому файлу и выберите 'Запуск от имени администратора'."
        ttk.Label(admin_frame, text=admin_text, wraplength=600).pack(anchor=tk.W)
        
        # Секция Проблемы OCR (Оптическое распознавание символов)
        ocr_frame = ttk.LabelFrame(scrollable_frame, text="Проблемы OCR (Оптическое распознавание символов)", padding="10")
        ocr_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Масштабирование
        scaling_frame = ttk.Frame(ocr_frame)
        scaling_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(scaling_frame, text="Масштабирование дисплея:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        scaling_text = "Установите масштабирование дисплея Windows на 100% (особенно важно для пользователей ноутбуков).\n" \
                       "Кратко: Щелкните правой кнопкой мыши на рабочем столе → Параметры дисплея → Масштаб → 100%"
        ttk.Label(scaling_frame, text=scaling_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Размер игрового интерфейса
        ui_size_frame = ttk.Frame(ocr_frame)
        ui_size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ui_size_frame, text="Размер внутриигрового интерфейса:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        ui_size_text = "Не делайте интерфейс в игре слишком маленьким. Чем меньше внутриигровой интерфейс, тем менее стабилен OCR.\n" \
                       "Настройка по умолчанию подходит, или немного меньше (максимум уменьшение на 10-20%)."
        ttk.Label(ui_size_frame, text=ui_size_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Разрешение игры
        resolution_frame = ttk.Frame(ocr_frame)
        resolution_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(resolution_frame, text="Разрешение игры:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        resolution_text = "Рекомендуемое разрешение игры: 1920x1080"
        ttk.Label(resolution_frame, text=resolution_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Шрифт
        font_frame = ttk.Frame(ocr_frame)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="Шрифт игры:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        font_text = "Используйте шрифт по умолчанию в игре: Tahoma"
        ttk.Label(font_frame, text=font_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Настройки задержки
        delay_frame = ttk.LabelFrame(scrollable_frame, text="Настройки задержки заполнителя коллекции", padding="10")
        delay_frame.pack(fill=tk.X, pady=(0, 10))
        
        delay_text = "Не устанавливайте задержку слишком низкой. Около 30 мс достаточно быстро. Если у вас плохой пинг, могут потребоваться более высокие значения."
        ttk.Label(delay_frame, text=delay_text, wraplength=600).pack(anchor=tk.W)
        
        # Изображения красных точек
        reddot_frame = ttk.LabelFrame(scrollable_frame, text="Изображения красных точек", padding="10")
        reddot_frame.pack(fill=tk.X, pady=(0, 10))
        
        reddot_text = "Файл изображения красной точки red-dot.png должен находиться в той же папке, что и исполняемый файл. Трекер коллекции ищет красную точку, чтобы определить, какие коллекции еще доступны для заполнения."
        ttk.Label(reddot_frame, text=reddot_text, wraplength=600).pack(anchor=tk.W)
