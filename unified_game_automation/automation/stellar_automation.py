# Stellar system automation logic
# Fully rewritten to remove Timer and make STOP work reliably

import time
import re
import threading
import os
import sys
from datetime import datetime
from tkinter import messagebox
from data.stellar_data import get_penetration_exceptions
from automation.base_automation import BaseAutomation


class StellarAutomation(BaseAutomation):
    def __init__(self, game_connector, ocr_engine, status_callback=None):
        super().__init__(game_connector, ocr_engine, status_callback)

        self.running = False
        self.stop_event = threading.Event()

        self.loop_in_progress = False
        self.wrong_read_counter = 0

        self.area = None
        self.imprint_button_coords = None
        self.stat_config = {}
        self.delay_ms = 800
        self.effect_delay_ms = 1000

        self.stat_counter = {}
        self.iteration_count = 0

        # Лог рядом с исполняемым файлом (работает и из exe и из исходников)
        if getattr(sys, 'frozen', False):
            # Запущено из PyInstaller exe
            exe_dir = os.path.dirname(sys.executable)
        else:
            # Запущено из исходников
            exe_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.log_file_path = os.path.join(exe_dir, "stellar_automation_log.txt")

    # -----------------------------
    # SETTERS
    # -----------------------------
    def set_area(self, area):
        self.area = area

    def set_imprint_button(self, coords):
        self.imprint_button_coords = coords

    def set_effect_delay(self, delay_ms):
        self.effect_delay_ms = delay_ms

    # -----------------------------
    # LOGGING
    # -----------------------------
    def update_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}"

        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except:
            pass

        if self.status_callback:
            self.status_callback(log_message)

    # -----------------------------
    # START / STOP
    # -----------------------------
    def start(self, stat_config):
        if not self.area:
            self.update_status("Set area first")
            return False

        if not self.imprint_button_coords:
            self.update_status("Set Imprint button first")
            return False

        self.stop_event.clear()

        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                self.update_status("Game not found")
                return False

        # normalize config
        self.stat_config = {}
        for stat_name, min_value in stat_config.items():
            name = stat_name.strip().lower()
            val = re.sub(r"\s+", "", min_value).lower() if min_value else ""
            self.stat_config[name] = val

        self.running = True
        self.wrong_read_counter = 0
        self.stat_counter = {}
        self.iteration_count = 0

        # clear log
        try:
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                f.write(
                    f"=== Stellar Automation Started at "
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                )
        except:
            pass

        self.update_status("[INFO] Starting automation loop...")

        threading.Thread(
            target=self._automation_loop,
            daemon=True
        ).start()

        return True

    def stop(self):
        self.running = False
        self.stop_event.set()
        self.update_status("Stellar automation stopped")

        if self.stat_counter:
            self.show_stats_summary()

    # -----------------------------
    # MAIN LOOP
    # -----------------------------
    def _automation_loop(self):
        time.sleep(3)

        while self.running and not self.stop_event.is_set():
            self.loop_ocr()

            # delay between rolls with stop checks
            for _ in range(int(self.delay_ms / 100)):
                if self.stop_event.is_set():
                    return
                time.sleep(0.1)

    # -----------------------------
    # ONE ITERATION
    # -----------------------------
    def loop_ocr(self):
        if self.stop_event.is_set() or not self.running:
            return

        if self.loop_in_progress:
            return

        self.loop_in_progress = True

        try:
            self.update_status(f"[DEBUG] Starting iteration #{self.iteration_count + 1}")

            # effect delay with stop checks
            for _ in range(int(self.effect_delay_ms / 100)):
                if self.stop_event.is_set():
                    self.loop_in_progress = False
                    return
                time.sleep(0.1)

            # click to clear effects
            if not self.game_connector.click_at_position(self.imprint_button_coords):
                self.update_status("[ERROR] Click failed")
                self.loop_in_progress = False
                return

            time.sleep(0.2)

            # screenshot
            screenshot = self.game_connector.capture_area_bitblt(self.area)
            if screenshot is None:
                self.update_status("[ERROR] Screenshot failed")
                self.stop()
                self.loop_in_progress = False
                return

            raw_text = self.ocr_engine.extract_text(screenshot)
            self.update_status(f"[DEBUG] Raw OCR text: '{raw_text.strip()}'")

            text = self.ocr_engine.parse_stellar_text(raw_text)
            self.update_status(f"[DEBUG] Parsed text: '{text}'")

            self.iteration_count += 1

            # extract number
            stat_value_match = re.search(r'\+\s*(\d+)', text)
            if stat_value_match:
                numbers_found = [stat_value_match.group(1)]
            else:
                all_numbers = re.findall(r'\d+', text)
                numbers_found = [all_numbers[-1]] if all_numbers else []

            self.update_status(f"[DEBUG] Extracted stat value(s): {numbers_found}")

            if len(numbers_found) != 1:
                self.wrong_read_counter += 1
                self.update_status(f"[WARN] Wrong number count: {len(numbers_found)} ({self.wrong_read_counter}/6)")
                if self.wrong_read_counter > 6:
                    self.update_status("[STOP] Too many OCR errors")
                    self.stop()
                self.loop_in_progress = False
                return

            self.wrong_read_counter = 0
            stat_value_detected = numbers_found[0]

            # extract stat name
            stat_match = re.search(r'(.+?)\s*\+?\s*\d+', text)
            stat_name_detected = stat_match.group(1).strip() if stat_match else None

            if stat_name_detected:
                key = f"{stat_name_detected} +{stat_value_detected}"
                self.stat_counter[key] = self.stat_counter.get(key, 0) + 1
                self.update_status(f"Roll #{self.iteration_count}: {key}")
            else:
                self.update_status(f"Roll #{self.iteration_count}: {text}")

            # check match
            found_match = False
            matched_stat = None

            lower_text = text.lower()

            for stat_name, min_value in self.stat_config.items():
                pattern = r"\b" + re.escape(stat_name) + r"\b"
                if re.search(pattern, lower_text):

                    if stat_name == "penetration":
                        exceptions = get_penetration_exceptions()
                        if any(exc in lower_text for exc in exceptions):
                            continue

                    value_ok = True
                    if min_value:
                        if min_value.isdigit():
                            value_ok = int(stat_value_detected) >= int(min_value)
                        else:
                            value_ok = min_value in lower_text

                    if value_ok:
                        found_match = True
                        matched_stat = stat_name
                        break

            if found_match:
                self.update_status(f"[SUCCESS] Found: {matched_stat} {stat_value_detected}")
                try:
                    messagebox.showinfo(
                        "Stellar Automation",
                        f"Desired stat found: {matched_stat} {stat_value_detected}"
                    )
                except:
                    pass

                self.stop()
                self.loop_in_progress = False
                return

        except Exception as e:
            import traceback
            self.update_status(f"[FATAL ERROR] {e}")
            self.update_status(traceback.format_exc())
            self.stop()

        self.loop_in_progress = False

    # -----------------------------
    # SUMMARY
    # -----------------------------
    def show_stats_summary(self):
        print("\n" + "=" * 60)
        print("STELLAR SYSTEM STATISTICS SUMMARY")
        print("=" * 60)

        total = sum(self.stat_counter.values())
        print(f"Total Rolls: {total}\n")

        for stat, count in sorted(self.stat_counter.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total else 0
            print(f"{stat:40s} × {count:3d} ({pct:5.1f}%)")

        print("=" * 60)
