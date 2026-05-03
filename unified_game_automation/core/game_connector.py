# Unified game connector with BitBlt capture
# Combines functionality from main.py GameConnector and arrival_skill_ocr/game_connector.py

from pywinauto import Application
import win32gui
import win32con
import win32ui
from ctypes import windll
from PIL import Image
from .clicking.clicking_config import get_clicker_class, get_clicker_name
import mss

class GameConnector:
    def __init__(self, status_callback=None):
        """Initialize the unified game connector"""
        self.game_window = None
        self.status_callback = status_callback
        self.clicker = None  # Will be initialized when connected to game

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def connect_to_game(self):
        """Connect to the game window by class name"""
        try:
            app = Application()
            app.connect(class_name="D3D Window")
            windows = app.windows(class_name="D3D Window")

            if len(windows) == 1:
                self.game_window = windows[0]
            elif len(windows) > 1:
                for window in windows:
                    window_text = window.window_text().lower()
                    if any(keyword in window_text for keyword in ["stellar", "game", "cabal"]):
                        self.game_window = window
                        break
                else:
                    for window in windows:
                        if window.is_visible():
                            self.game_window = window
                            break
                    else:
                        self.game_window = windows[0]
            else:
                raise Exception("No D3D Window found")

            if self.game_window.is_visible() and self.game_window.is_enabled():
                # Initialize the clicker with the connected game window
                clicker_class = get_clicker_class()
                self.clicker = clicker_class(
                    game_window=self.game_window,
                    get_offset_callback=self.get_window_client_offset
                )
                clicker_name = get_clicker_name()
                self.update_status(f"Connected to game using {clicker_name}")
                return True
            else:
                raise Exception("Found window but it's not visible or enabled")

        except Exception as e:
            self.update_status(f"Could not connect to the game. Make sure it's running. Error: {str(e)}")
            return False

    def click_at_position(self, coords, adjust_for_client_area=True):
        """Click at the specified coordinates in the game window using the active clicking strategy"""
        if not self.clicker:
            self.update_status("Click failed: Not connected to game")
            return False
        
        try:
            return self.clicker.click(coords, adjust_for_client_area)
        except Exception as e:
            self.update_status(f"Click failed: {str(e)}")
            return False

    def right_click_at_position(self, coords, adjust_for_client_area=True):
        """Right-click at the specified coordinates in the game window using the active clicking strategy"""
        if not self.clicker:
            self.update_status("Right-click failed: Not connected to game")
            return False
        
        try:
            return self.clicker.right_click(coords, adjust_for_client_area)
        except Exception as e:
            self.update_status(f"Right-click failed: {str(e)}")
            return False
    
    def middle_click_at_position(self, coords, adjust_for_client_area=True):
        """Middle-click at the specified coordinates in the game window using the active clicking strategy"""
        if not self.clicker:
            self.update_status("Middle-click failed: Not connected to game")
            return False
        
        try:
            return self.clicker.middle_click(coords, adjust_for_client_area)
        except Exception as e:
            self.update_status(f"Middle-click failed: {str(e)}")
            return False

    def get_window_rect(self):
        """Get the rectangle of the game window"""
        if not self.game_window:
            return None
        try:
            return self.game_window.rectangle()
        except Exception:
            return None

    def get_client_rect(self):
        """Get the client rectangle of the game window"""
        if not self.game_window:
            return None
        try:
            hwnd = self.game_window.handle
            client_rect = win32gui.GetClientRect(hwnd)
            client_pos = win32gui.ClientToScreen(hwnd, (0, 0))
            return (
                client_pos[0],
                client_pos[1],
                client_pos[0] + client_rect[2],
                client_pos[1] + client_rect[3]
            )
        except Exception as e:
            self.update_status(f"Failed to get client rect: {str(e)}")
            return None

    def get_window_client_offset(self):
        """Calculate the offset between window coordinates and client coordinates"""
        if not self.game_window:
            return None
        try:
            window_rect = self.get_window_rect()
            client_rect = self.get_client_rect()
            if not window_rect or not client_rect:
                return None
            offset_x = client_rect[0] - window_rect.left
            offset_y = client_rect[1] - window_rect.top
            return (offset_x, offset_y)
        except Exception as e:
            self.update_status(f"Failed to calculate window-client offset: {str(e)}")
            return None

    def convert_to_window_coords(self, screen_x, screen_y):
        """Convert screen coordinates to window-relative coordinates"""
        if not self.game_window:
            return (screen_x, screen_y, False)
        try:
            rect = self.game_window.rectangle()
            rel_x = screen_x - rect.left
            rel_y = screen_y - rect.top
            return (rel_x, rel_y, True)
        except Exception:
            return (screen_x, screen_y, False)

    def is_connected(self):
        """Check if connected to game window"""
        return self.game_window is not None
    
    def get_game_window(self):
        """Get the pywinauto game window object"""
        return self.game_window

    def capture_area_bitblt(self, area):
        """
        Capture a specific area - пробует mss (экран), fallback на BitBlt (окно)
        Args:
            area: Tuple of (left, top, width, height) in screen coordinates
        Returns:
            PIL Image or None if capture failed
        """
        if not self.game_window:
            return None
        
        # Сначала пробуем mss (работает с экранными координатами напрямую)
        try:
            img = self.capture_area_mss(area)
            if img:
                return img
        except:
            pass
        
        # Fallback на BitBlt (если mss не сработал)
        try:
            hwnd = self.game_window.handle

            if win32gui.IsIconic(hwnd):
                return None

            # Получаем координаты окна
            win_left, win_top, win_right, win_bottom = win32gui.GetWindowRect(hwnd)
            
            # Вычисляемую нужную область относительно экрана
            area_left, area_top, area_width, area_height = area
            
            # DEBUG: Выводим информацию для отладки
            print(f"📸 Capture (BitBlt fallback): window=({win_left}, {win_top}, {win_right}, {win_bottom})")
            print(f"📸 Area: ({area_left}, {area_top}, {area_width}x{area_height})")
            
            # Вычисляем координаты относительно окна
            rel_left = area_left - win_left
            rel_top = area_top - win_top
            
            # Проверяем, что область в пределах окна
            if rel_left < 0 or rel_top < 0 or rel_left + area_width > (win_right - win_left) or rel_top + area_height > (win_bottom - win_top):
                print(f"⚠️  Area out of bounds, using fallback method")
                # Если область выходит за пределы окна, захватываем всё окно и обрезаем
                return self._capture_full_window_and_crop(hwnd, win_left, win_top, win_right, win_bottom, 
                                                         area_left, area_top, area_width, area_height)
            
            # Захватываем ТОЛЬКО нужную область (оптимизировано)
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, area_width, area_height)
            saveDC.SelectObject(saveBitMap)

            result = windll.gdi32.BitBlt(saveDC.GetSafeHdc(), 0, 0, area_width, area_height,
                                       hwndDC, rel_left, rel_top, win32con.SRCCOPY)

            if result:
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                                      bmpstr, 'raw', 'BGRX', 0, 1)

                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)

                return img

        except Exception as e:
            # Fallback на метод с захватом полного окна
            try:
                return self._capture_full_window_and_crop(hwnd, win_left, win_top, win_right, win_bottom,
                                                         area_left, area_top, area_width, area_height)
            except:
                pass

        return None
    
    def _capture_full_window_and_crop(self, hwnd, win_left, win_top, win_right, win_bottom,
                                     area_left, area_top, area_width, area_height):
        """Захватывает всё окно и обрезает до нужной области (fallback метод)"""
        try:
            width = win_right - win_left
            height = win_bottom - win_top

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = windll.gdi32.BitBlt(saveDC.GetSafeHdc(), 0, 0, width, height,
                                       hwndDC, 0, 0, win32con.SRCCOPY)

            if result:
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                full_image = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                                            bmpstr, 'raw', 'BGRX', 0, 1)

                rel_left = area_left - win_left
                rel_top = area_top - win_top

                cropped = full_image.crop((rel_left, rel_top,
                                         rel_left + area_width,
                                         rel_top + area_height))

                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)

                return cropped

        except Exception:
            pass

        try:
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
        except:
            pass

        return None
    
    def capture_area_mss(self, area):
        """
        Захватывает область экрана через mss (быстро и надёжно)
        Args:
            area: Tuple of (left, top, width, height) in screen coordinates
        Returns:
            PIL Image or None if capture failed
        """
        try:
            area_left, area_top, area_width, area_height = area
            
            with mss.mss() as sct:
                monitor = {
                    "top": area_top,
                    "left": area_left,
                    "width": area_width,
                    "height": area_height
                }
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                return img
        except Exception as e:
            print(f"❌ MSS capture failed: {e}")
            return None
