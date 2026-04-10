# Help tab UI - Помощь
# Provides brief explanations of what each tab does

import tkinter as tk
from tkinter import ttk
import webbrowser

class HelpTab:
    def __init__(self, parent_frame, main_window):
        """Инициализация вкладки Помощь"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Создание UI
        self.create_ui()

    def create_ui(self):
        """Создание UI помощи"""
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

        # ====== Звёздная Россыпь ======
        stellar_frame = ttk.LabelFrame(scrollable_frame, text="⭐ Звёздная Россыпь", padding="15")
        stellar_frame.pack(fill=tk.X, pady=(0, 15))

        stellar_text = ("Автоматизирует повторную выборку статов звездной россыпи. "
                       "Обнаруживает статы с помощью OCR и автоматически применяет их, "
                       "когда находит нужный.\n\n"
                       "✨ Возможности:\n"
                       "• Поддерживает пользовательские статы - вы можете определить свои собственные названия\n"
                       "• Можно искать несколько статов одновременно (логика ИЛИ - остановится на любом совпадении)\n"
                       "• Настраиваемые минимальные значения для каждого стата\n\n"
                       "📹 Видео с инструкцией:")
        ttk.Label(stellar_frame, text=stellar_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W)

        def open_stellar_video(event):
            webbrowser.open("https://www.youtube.com/watch?v=0KVkZXdlfyY")

        stellar_link = ttk.Label(stellar_frame, 
                               text="🔗 https://www.youtube.com/watch?v=0KVkZXdlfyY",
                               foreground=self.main_window.colors['accent'], 
                               cursor="hand2", 
                               font=("Segoe UI", 9, "underline"))
        stellar_link.pack(anchor=tk.W, pady=(8, 0))
        stellar_link.bind("<Button-1>", open_stellar_video)

        # ====== Пользовательские статы ======
        custom_stats_frame = ttk.LabelFrame(scrollable_frame, text="💡 Пользовательские статы", padding="15")
        custom_stats_frame.pack(fill=tk.X, pady=(0, 15))

        custom_stats_text = ("Пользовательские статы используют поиск подстроки для нахождения статов в игре.\n\n"
                           "🔍 Как это работает:\n"
                           "Инструмент ищет ваш текст в любом месте названия стата. "
                           "Например, если вы введёте 'Атака', он найдёт все статы содержащие это слово:\n"
                           "  • 'Увеличение всей атаки'\n"
                           "  • 'Шанс атаки'\n"
                           "  • Любой другой стат со словом 'Атака'\n\n"
                           "✨ Вам не нужно вводить точное полное название - просто укажите уникальную часть.")
        ttk.Label(custom_stats_frame, text=custom_stats_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W)

        # ====== Важные заметки ======
        notes_frame = ttk.LabelFrame(scrollable_frame, text="⚠️ Важные заметки", padding="15")
        notes_frame.pack(fill=tk.X, pady=(0, 10))

        notes_text = ("• Аварийная остановка: Нажмите ESC для немедленной остановки\n"
                     "• Несколько статов: При поиске нескольких статов автоматизация использует "
                     "логику ИЛИ - остановится, как только ЛЮБОЙ из указанных статов совпадёт\n"
                     "• Координаты кнопок: Все координаты сохраняются автоматически и восстанавливаются "
                     "при следующем запуске")
        ttk.Label(notes_frame, text=notes_text, wraplength=650,
                 font=self.main_window.default_font).pack(anchor=tk.W)
