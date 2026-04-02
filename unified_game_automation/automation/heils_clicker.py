import threading
import time
import win32gui


class HeilsClickerAutomation:
    """Simple continuous clicker using the game's configured clicker (background-friendly)."""

    def __init__(self, game_connector, status_callback=None):
        self.game_connector = game_connector
        self.status_callback = status_callback
        self.click_position = None
        self.delay_ms = 200  # default 200ms
        self.running = False
        self._thread = None

    def update_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def set_click_position(self, coords):
        """Set the window-relative click coordinates"""
        self.click_position = coords

    def set_delay_ms(self, delay_ms):
        """Set delay between clicks in milliseconds"""
        try:
            delay_ms = max(0, int(delay_ms))
        except Exception:
            delay_ms = 0
        self.delay_ms = delay_ms

    def _ensure_connected(self):
        """Ensure connection to game window"""
        if self.game_connector.is_connected():
            return True
        return self.game_connector.connect_to_game()

    def start(self):
        """Start clicking loop"""
        if not self.click_position:
            self.update_status("Set click position first")
            return False

        if not self._ensure_connected():
            self.update_status("Game not connected")
            return False

        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.update_status("Heils Clicker started")
        return True

    def _is_minimized(self):
        """Check if the game window is minimized"""
        try:
            game_window = self.game_connector.get_game_window()
            if game_window:
                hwnd = game_window.handle
                return win32gui.IsIconic(hwnd)
        except Exception:
            pass
        return False

    def _loop(self):
        while self.running:
            if not self.game_connector.is_connected():
                self.update_status("Lost game connection; stopping")
                self.running = False
                break
            try:
                # Use the configured clicker (PostMessage/SendMessage/pywinauto) so minimized windows work
                # Coordinates are the captured window-relative values; clicker will adjust client offset.
                coords = self.click_position

                # Windowed + minimized needs a small title-bar correction
                if self._is_minimized():
                    coords = (coords[0], coords[1] - 20)
                    if coords[1] < 0:
                        coords = (coords[0], 0)

                if not self.game_connector.click_at_position(coords, adjust_for_client_area=True):
                    self.update_status("Click failed")
            except Exception as e:
                self.update_status(f"Click failed: {str(e)}")
            
            time.sleep(self.delay_ms / 1000.0 if self.delay_ms >= 0 else 0)
        self.update_status("Heils Clicker stopped")

    def stop(self):
        self.running = False

    def emergency_stop(self):
        self.stop()
        self.update_status("🚨 Heils Clicker emergency stopped")

