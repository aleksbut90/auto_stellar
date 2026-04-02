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
        
        # Секция Крылья Силы
        arrival_frame = ttk.LabelFrame(scrollable_frame, text="Крылья Силы", padding="10")
        arrival_frame.pack(fill=tk.X, pady=(0, 10))
        
        arrival_text = "Автоматизирует повторную выборку навыков прибытия. Обнаруживает статы с помощью OCR и применяет/меняет навыки согласно вашим критериям.\n\n" \
                      "• Поддерживает пользовательские статы - вы можете определить свои собственные названия статистик для поиска\n" \
                      "• Можно искать несколько статов одновременно (условие ИЛИ - останавливается при совпадении любого стата)\n" \
                      "• Особый случай: 'Время перезарядки навыка прибытия уменьшено' требует область OCR ранга (здесь отображается 1-й ранг, 2-й ранг и т.д.)\n\n" \
                      "Видео настройки:"
        ttk.Label(arrival_frame, text=arrival_text, wraplength=600).pack(anchor=tk.W)
        
        def open_arrival_video(event):
            webbrowser.open("https://www.youtube.com/watch?v=PpWnRMNUtG8")
        
        arrival_link = ttk.Label(arrival_frame, text="https://www.youtube.com/watch?v=PpWnRMNUtG8", 
                               foreground="blue", cursor="hand2", font=("Arial", 9, "underline"))
        arrival_link.pack(anchor=tk.W, pady=(5, 0))
        arrival_link.bind("<Button-1>", open_arrival_video)
        
        # Секция Звездная Россыпь
        stellar_frame = ttk.LabelFrame(scrollable_frame, text="Звездная Россыпь", padding="10")
        stellar_frame.pack(fill=tk.X, pady=(0, 10))
        
        stellar_text = "Автоматизирует повторную выборку статов звездной россыпи. Обнаруживает статы с помощью OCR.\n\n" \
                      "• Поддерживает пользовательские статы - вы можете определить свои собственные названия статистик для поиска\n" \
                      "• Можно искать несколько статов одновременно (условие ИЛИ - останавливается при совпадении любого стата)\n\n" \
                      "Видео настройки:"
        ttk.Label(stellar_frame, text=stellar_text, wraplength=600).pack(anchor=tk.W)
        
        def open_stellar_video(event):
            webbrowser.open("https://www.youtube.com/watch?v=0KVkZXdlfyY")
        
        stellar_link = ttk.Label(stellar_frame, text="https://www.youtube.com/watch?v=0KVkZXdlfyY", 
                               foreground="blue", cursor="hand2", font=("Arial", 9, "underline"))
        stellar_link.pack(anchor=tk.W, pady=(5, 0))
        stellar_link.bind("<Button-1>", open_stellar_video)
        
        # Секция Заполнитель Коллекции
        collection_frame = ttk.LabelFrame(scrollable_frame, text="Заполнитель Коллекции", padding="10")
        collection_frame.pack(fill=tk.X, pady=(0, 10))
        
        collection_text = "Автоматизирует заполнение коллекции путем обнаружения красных точек и прокликивания страниц.\n\n" \
                         "Видео настройки:"
        ttk.Label(collection_frame, text=collection_text, wraplength=600).pack(anchor=tk.W)
        
        def open_collection_video(event):
            webbrowser.open("https://youtu.be/mPaBDvGdkTA")
        
        collection_link = ttk.Label(collection_frame, text="https://youtu.be/mPaBDvGdkTA", 
                                   foreground="blue", cursor="hand2", font=("Arial", 9, "underline"))
        collection_link.pack(anchor=tk.W, pady=(5, 0))
        collection_link.bind("<Button-1>", open_collection_video)
        
        # Секция Heils Кликер
        heils_frame = ttk.LabelFrame(scrollable_frame, text="Heils Кликер", padding="10")
        heils_frame.pack(fill=tk.X, pady=(0, 10))
        
        heils_text = "Простой кликер, который непрерывно кликает по заданной координате до остановки."
        ttk.Label(heils_frame, text=heils_text, wraplength=600).pack(anchor=tk.W)
        
        # Секция Пользовательские статы
        custom_stats_frame = ttk.LabelFrame(scrollable_frame, text="Пользовательские статы", padding="10")
        custom_stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        custom_stats_text = "Пользовательские статы используют поиск подстроки для нахождения статов в игре.\n\n" \
                           "Это означает, что инструмент ищет ваш текст в любом месте названия стата, которое отображается в игре. " \
                           "Например, если вы введете 'Атака', он найдет такие статы как 'Увеличение всей атаки', 'Шанс атаки' или любой стат, содержащий слово 'Атака'.\n\n" \
                           "Вам не нужно вводить точное полное название стата - просто введите уникальную часть названия стата, который хотите найти."
        ttk.Label(custom_stats_frame, text=custom_stats_text, wraplength=600).pack(anchor=tk.W)
        
        # Секция Важные заметки
        notes_frame = ttk.LabelFrame(scrollable_frame, text="Важные заметки", padding="10")
        notes_frame.pack(fill=tk.X, pady=(0, 10))
        
        notes_text = "• Крылья Силы: Область OCR 'Ранг' специально предназначена для стата 'Время перезарядки навыка прибытия уменьшено', " \
                    "который нельзя обнаружить по значению стата и требует обнаружения по рангу\n" \
                    "• Несколько статов: При поиске нескольких статов автоматизация использует логику ИЛИ - " \
                    "она остановится, как только ЛЮБОЙ из указанных статов совпадет с вашими критериями"
        ttk.Label(notes_frame, text=notes_text, wraplength=600).pack(anchor=tk.W)
