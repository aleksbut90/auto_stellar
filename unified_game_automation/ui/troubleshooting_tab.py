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
        main_frame = ttk.Frame(self.parent_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Создание прокручиваемого фрейма
        canvas = tk.Canvas(main_frame, highlightthickness=0)
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

        # ====== Запуск от имени администратора ======
        admin_frame = ttk.LabelFrame(scrollable_frame, text="🔐 Запуск от имени администратора", padding="15")
        admin_frame.pack(fill=tk.X, pady=(0, 15))

        admin_text = ("⚠️ Приложение должно быть запущено от имени администратора для корректной работы.\n\n"
                     "📌 Как запустить:\n"
                     "Щёлкните правой кнопкой мыши по исполняемому файлу → "
                     "'Запуск от имени администратора'")
        ttk.Label(admin_frame, text=admin_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W)

        # ====== Проблемы OCR ======
        ocr_frame = ttk.LabelFrame(scrollable_frame, text="👁️ Проблемы с распознаванием текста (OCR)", padding="15")
        ocr_frame.pack(fill=tk.X, pady=(0, 15))

        # Масштабирование
        scaling_frame = ttk.Frame(ocr_frame)
        scaling_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(scaling_frame, text="📐 Масштабирование дисплея:", 
                 font=self.main_window.heading_font).pack(anchor=tk.W)
        scaling_text = ("Установите масштабирование дисплея Windows на 100% "
                       "(особенно важно для пользователей ноутбуков).\n\n"
                       "📝 Инструкция:\n"
                       "Правой кнопкой на рабочем столе → Параметры дисплея → "
                       "Масштаб → 100%")
        ttk.Label(scaling_frame, text=scaling_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W, pady=(5, 0))

        # Размер игрового интерфейса
        ui_size_frame = ttk.Frame(ocr_frame)
        ui_size_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(ui_size_frame, text="🎮 Размер внутриигрового интерфейса:", 
                 font=self.main_window.heading_font).pack(anchor=tk.W)
        ui_size_text = ("Не делайте интерфейс в игре слишком маленьким. "
                       "Чем меньше интерфейс, тем менее стабильно работает OCR.\n\n"
                       "✅ Рекомендуемые настройки:\n"
                       "По умолчанию или немного меньше (максимум уменьшение на 10-20%).")
        ttk.Label(ui_size_frame, text=ui_size_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W, pady=(5, 0))

        # Разрешение игры
        resolution_frame = ttk.Frame(ocr_frame)
        resolution_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(resolution_frame, text="🖥️ Разрешение игры:", 
                 font=self.main_window.heading_font).pack(anchor=tk.W)
        resolution_text = "✅ Рекомендуемое разрешение: 1920x1080"
        ttk.Label(resolution_frame, text=resolution_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W, pady=(5, 0))

        # Шрифт
        font_frame = ttk.Frame(ocr_frame)
        font_frame.pack(fill=tk.X)

        ttk.Label(font_frame, text="🔤 Шрифт игры:", 
                 font=self.main_window.heading_font).pack(anchor=tk.W)
        font_text = "✅ Используйте шрифт по умолчанию в игре: Tahoma"
        ttk.Label(font_frame, text=font_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W, pady=(5, 0))

        # ====== Дополнительные рекомендации ======
        tips_frame = ttk.LabelFrame(scrollable_frame, text="💡 Дополнительные рекомендации", padding="15")
        tips_frame.pack(fill=tk.X, pady=(0, 10))

        tips_text = ("🚀 Оптимизация производительности:\n\n"
                    "• Не устанавливайте задержку слишком низкой\n"
                    "  - Для быстрого интернета: около 30 мс\n"
                    "  - При плохом пинге: используйте более высокие значения (100-500 мс)\n\n"
                    "• Файл red-dot.png должен находиться в той же папке, что и исполняемый файл\n"
                    "  - Этот файл используется для обнаружения незаполненных коллекций\n\n"
                    "• При проблемах с OCR попробуйте:\n"
                    "  - Перезапустить приложение\n"
                    "  - Переопределить область OCR\n"
                    "  - Проверить что игра в окне и не свёрнута")
        ttk.Label(tips_frame, text=tips_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W)
