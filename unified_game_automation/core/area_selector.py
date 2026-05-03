"""
Area Selector — ЧИСТЫЙ tkinter, абсолютные координаты
"""

import tkinter as tk
from tkinter import messagebox
import pyautogui
import ctypes


class AreaSelector:
    def __init__(self, root, callback=None):
        self.root = root
        self.callback = callback
    
    def _get_dpi_scale(self):
        """Получить фактор масштабирования DPI"""
        try:
            # Получаем DPI экрана
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX = 88
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0  # 96 DPI = 100%
        except:
            return 1.0
    
    def select_area(self):
        """Начать выделение области"""
        # Устанавливаем DPI-aware режим для корректной работы
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass
        
        # Полноэкранное окно
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)
        overlay.configure(bg='#202020')
        overlay.attributes('-alpha', 0.25)
        overlay.configure(cursor='crosshair')
        
        # Canvas
        canvas = tk.Canvas(overlay, bg='gray', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Подсказка
        canvas.create_text(
            overlay.winfo_screenwidth() // 2, 40,
            text="Зажми ЛКМ и тяни | ESC — отмена",
            fill='white', font=('Segoe UI', 16, 'bold')
        )
        
        # Данные
        state = {'x1': 0, 'y1': 0, 'rect': None}
        
        def on_press(event):
            # Получаем РЕАЛЬНЮ позицию мыши через pyautogui
            mx, my = pyautogui.position()
            state['x1'] = mx
            state['y1'] = my
            
            if state['rect']:
                canvas.delete(state['rect'])
            
            state['rect'] = canvas.create_rectangle(
                mx, my, mx, my,
                outline='red', width=3
            )
            print(f"📍 Press: pyautogui=({mx}, {my}), event.x_root={event.x_root}, event.y_root={event.y_root}")
        
        def on_drag(event):
            if state['rect']:
                # Используем pyautogui для получения РЕАЛЬНЫХ экранных координат
                mx, my = pyautogui.position()
                
                canvas.coords(state['rect'], state['x1'], state['y1'], mx, my)
        
        def on_release(event):
            try:
                # Получаем ФИНАЛЬНЮ позицию через pyautogui
                end_x, end_y = pyautogui.position()
                x1 = state['x1']
                y1 = state['y1']

                # Вычисляем координаты (pyautogui уже возвращает реальные пиксели)
                left = min(x1, end_x)
                top = min(y1, end_y)
                width = abs(end_x - x1)
                height = abs(end_y - y1)

                print(f"📍 Start: ({x1}, {y1})")
                print(f"📍 End: ({end_x}, {end_y})")
                print(f"📏 Result: left={left}, top={top}, w={width}, h={height}")

                overlay.destroy()

                if width < 10 or height < 10:
                    messagebox.showwarning("Маленькая область", "Выдели область побольше!")
                    return

                # Preview
                self._show_preview(left, top, width, height)

                if self.callback:
                    self.callback((left, top, width, height))

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                try:
                    overlay.destroy()
                except:
                    pass
        
        def on_esc(event):
            try:
                overlay.destroy()
            except:
                pass
        
        canvas.bind('<Button-1>', on_press)
        canvas.bind('<B1-Motion>', on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)
        overlay.bind('<Escape>', on_esc)
    
    def _show_preview(self, x, y, w, h):
        """Показать красную рамку"""
        try:
            preview = tk.Toplevel(self.root)
            preview.overrideredirect(True)
            preview.attributes("-topmost", True)
            preview.geometry(f"{w}x{h}+{x}+{y}")
            
            canvas = tk.Canvas(preview, bg='black', highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            canvas.create_rectangle(0, 0, w, h, outline="red", width=3)
            
            self.root.after(2000, preview.destroy)
        except Exception as e:
            print(f"Preview error: {e}")
