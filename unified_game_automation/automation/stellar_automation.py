# Stellar system automation logic
# Extracted from main.py

import time
import re
import threading
import os
from datetime import datetime
from tkinter import messagebox
from data.stellar_data import get_penetration_exceptions
from automation.base_automation import BaseAutomation

class StellarAutomation(BaseAutomation):
    def __init__(self, game_connector, ocr_engine, status_callback=None):
        """Initialize stellar system automation"""
        super().__init__(game_connector, ocr_engine, status_callback)

        # Automation state
        self.loop_in_progress = False
        self.wrong_read_counter = 0

        # Configuration
        self.area = None
        self.imprint_button_coords = None
        self.stat_config = {}  # Dictionary: {stat_name: min_value}
        self.delay_ms = 800  # Simplified - removed ping dependency
        self.effect_delay_ms = 1000  # Default 1 second for visual effect clearing
        
        # Stat tracking
        self.stat_counter = {}
        self.iteration_count = 0
        
        # Log file path
        self.log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log.txt")

    def set_area(self, area):
        """Set the OCR area"""
        self.area = area

    def set_imprint_button(self, coords):
        """Set the imprint button coordinates"""
        self.imprint_button_coords = coords

    def set_effect_delay(self, delay_ms):
        """Set the visual effect clearing delay in milliseconds"""
        self.effect_delay_ms = delay_ms

    def start(self, stat_config):
        """Start the stellar automation
        
        Args:
            stat_config: Dictionary of {stat_name: min_value} (OR logic - any match is accepted)
                        min_value can be empty string if no minimum required
        """
        if not self.area:
            self.update_status("Set area first")
            return False

        if not self.imprint_button_coords:
            self.update_status("Set Imprint button first")
            return False

        # Connect to game if not already connected
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                self.update_status("Game not found")
                return False

        # Normalize stat config (remove spaces, lowercase)
        self.stat_config = {}
        for stat_name, min_value in stat_config.items():
            normalized_name = re.sub(r"\s+", "", stat_name).lower()
            normalized_value = re.sub(r"\s+", "", min_value).lower() if min_value else ""
            self.stat_config[normalized_name] = normalized_value

        stats_display = " OR ".join([f"{name}(≥{val})" if val else name 
                                    for name, val in stat_config.items()])
        self.update_status(f"Looking for: {stats_display}")

        self.running = True
        self.wrong_read_counter = 0
        self.stat_counter = {}
        self.iteration_count = 0

        # Start automation in thread
        threading.Thread(target=self._start_automation_loop, daemon=True).start()
        return True

    def update_status(self, message):
        """Update status with logging to file"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}"
        
        # Write to log file
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception:
            pass
        
        # Call parent status callback if exists
        if self.status_callback:
            self.status_callback(log_message)

    def _start_automation_loop(self):
        """Start the automation loop with initial delay"""
        # Clear log file at start
        try:
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                f.write(f"=== Stellar Automation Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        except Exception:
            pass
        
        self.update_status("[INFO] Starting automation loop...")
        time.sleep(3)  # Initial delay
        self.loop_ocr()

    def stop(self):
        """Stop the stellar automation"""
        self.running = False
        self.update_status("Stellar automation stopped")
        if self.stat_counter:
            self.show_stats_summary()

    @staticmethod
    def numeric_compare(option_min_value_int, text):
        """Compare numbers in text with minimum value"""
        numbers_found = re.findall(r"\d+", text)
        for num_str in numbers_found:
            val = int(num_str)
            if val >= option_min_value_int:
                return True
        return False

    def loop_ocr(self):
        """Main OCR loop - extracted from main.py"""
        if self.loop_in_progress:
            return

        if not self.running:
            return

        self.loop_in_progress = True

        try:
            # Log iteration start
            self.update_status(f"[DEBUG] Starting iteration #{self.iteration_count + 1}")
            
            # Wait for visual effects to appear, then click to close them
            self.update_status(f"[DEBUG] Waiting {self.effect_delay_ms/1000}s for effects")
            time.sleep(self.effect_delay_ms / 1000.0)

            # Click imprint button (which becomes "close" button) to clear visual effects
            self.update_status(f"[DEBUG] Clicking imprint button at {self.imprint_button_coords}")
            if not self.game_connector.click_at_position(self.imprint_button_coords):
                self.update_status("[ERROR] Click failed - check coordinates and window focus")
                self.loop_in_progress = False
                return

            # Small delay to let effects clear
            time.sleep(0.2)

            # Capture screenshot using BitBlt
            self.update_status(f"[DEBUG] Capturing area: {self.area}")
            screenshot = self.game_connector.capture_area_bitblt(self.area)
            if screenshot is None:
                self.update_status("[ERROR] Screenshot capture failed - check area and window")
                self.stop()
                self.loop_in_progress = False
                return

            # Extract text using Tesseract
            raw_text = self.ocr_engine.extract_text(screenshot)
            self.update_status(f"[DEBUG] Raw OCR text: '{raw_text.strip()}'")

            text = self.ocr_engine.parse_stellar_text(raw_text)
            self.update_status(f"[DEBUG] Parsed text: '{text}'")
            
            self.iteration_count += 1

            # Check for exactly one number (stellar format validation)
            numbers_found = self.ocr_engine.find_numbers(text)
            self.update_status(f"[DEBUG] Numbers found: {numbers_found} (count: {len(numbers_found)})")

            if len(numbers_found) != 1:
                self.wrong_read_counter += 1
                self.update_status(f"[WARN] Wrong number count: {len(numbers_found)}, counter: {self.wrong_read_counter}/6")
                if self.wrong_read_counter > 6:
                    self.update_status("[STOP] Too many OCR errors - check area definition")
                    self.stop()
                    self.loop_in_progress = False
                    return
                else:
                    self.loop_in_progress = False
                    # Schedule next attempt with longer delay
                    self.update_status(f"[DEBUG] Retrying in 0.7s...")
                    threading.Timer(0.7, self.loop_ocr).start()
                    return

            self.wrong_read_counter = 0

            # Extract stat name and value from text for display and tracking
            # Parse the text to get stat name and value (format: "Stat Name +Value" or "Stat Name Value")
            stat_name_detected = None
            stat_value_detected = None
            numbers_found = re.findall(r"\d+", text)
            if numbers_found:
                stat_value_detected = numbers_found[0]
            
            # Try to extract stat name (everything before the number)
            stat_match = re.search(r'(.+?)\s*\+?\s*\d+', text)
            if stat_match:
                stat_name_detected = stat_match.group(1).strip()
            
            # Track this roll
            if stat_name_detected and stat_value_detected:
                stat_key = f"{stat_name_detected} +{stat_value_detected}"
                self.stat_counter[stat_key] = self.stat_counter.get(stat_key, 0) + 1
                # Display clean stat info
                self.update_status(f"Roll #{self.iteration_count}: {stat_name_detected} +{stat_value_detected}")
            elif stat_name_detected:
                stat_key = f"{stat_name_detected}"
                self.stat_counter[stat_key] = self.stat_counter.get(stat_key, 0) + 1
                self.update_status(f"Roll #{self.iteration_count}: {stat_name_detected}")
            else:
                self.update_status(f"Roll #{self.iteration_count}: {text}")

            # Check if any stat matches with its individual minimum value (OR logic)
            found_match = False
            matched_stat = None
            matched_value = None
            
            self.update_status(f"[DEBUG] Checking against config: {self.stat_config}")
            
            if self.stat_config:
                for stat_name, min_value in self.stat_config.items():
                    self.update_status(f"[DEBUG] Checking stat '{stat_name}' (min: {min_value})")
                    
                    # Check if stat name is in text
                    if stat_name in text:
                        self.update_status(f"[DEBUG] Stat name '{stat_name}' FOUND in text")
                        
                        # Special handling for penetration exceptions
                        if stat_name == "penetration":
                            exceptions = get_penetration_exceptions()
                            if any(exc in text for exc in exceptions):
                                self.update_status("[DEBUG] Ignoring penetration exception")
                                continue
                        
                        # Check minimum value for this specific stat
                        value_matches = True
                        if min_value:
                            self.update_status(f"[DEBUG] Checking min value: {min_value}")
                            if min_value.isdigit():
                                min_val_int = int(min_value)
                                value_matches = self.numeric_compare(min_val_int, text)
                                self.update_status(f"[DEBUG] Numeric compare result: {value_matches}")
                            else:
                                value_matches = (min_value in text)
                                self.update_status(f"[DEBUG] String compare result: {value_matches}")
                        else:
                            self.update_status("[DEBUG] No min value required")
                        
                        # If both stat name and value match (or no value required), we found it!
                        if value_matches:
                            self.update_status(f"[SUCCESS] Match found: {stat_name}")
                            found_match = True
                            matched_stat = stat_name
                            # Extract the actual value from text for display
                            matched_value = stat_value_detected if stat_value_detected else "N/A"
                            break
                    else:
                        self.update_status(f"[DEBUG] Stat name '{stat_name}' NOT in text")

            # Check success conditions
            if found_match:
                min_val_display = self.stat_config.get(matched_stat, "")
                if min_val_display:
                    self.update_status(f"[SUCCESS] Found: {matched_stat} {matched_value} (≥{min_val_display})")
                else:
                    self.update_status(f"[SUCCESS] Found: {matched_stat} {matched_value}")
                try:
                    # Notify user of success so they can stop watching the log
                    messagebox.showinfo(
                        "Stellar Automation",
                        f"Desired stat found: {matched_stat} {matched_value}"
                        + (f" (≥{min_val_display})" if min_val_display else "")
                    )
                except Exception:
                    # Keep automation flow even if UI notification fails
                    pass
                self.stop()
            else:
                self.update_status("[DEBUG] No match found, continuing...")
                # Continue automation - click imprint button
                if not self.game_connector.is_connected():
                    if not self.game_connector.connect_to_game():
                        self.update_status("[ERROR] Connection failed")
                        self.stop()
                        return

                # Double click with delay (as in original)
                self.update_status(f"[DEBUG] Double-clicking imprint button at {self.imprint_button_coords}")
                if not self.game_connector.click_at_position(self.imprint_button_coords):
                    self.update_status("[ERROR] First click failed")

                time.sleep(0.3)

                if not self.game_connector.click_at_position(self.imprint_button_coords):
                    self.update_status("[ERROR] Second click failed")

                self.loop_in_progress = False
                # Schedule next iteration
                self.update_status(f"[DEBUG] Scheduling next iteration in {self.delay_ms}ms")
                threading.Timer(self.delay_ms / 1000, self.loop_ocr).start()
                return

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            self.update_status(f"[FATAL ERROR] {str(e)}")
            self.update_status(f"[TRACE] {error_trace}")
            self.stop()

        self.loop_in_progress = False
    
    def show_stats_summary(self):
        """Show summary of detected stats in console/terminal"""
        print("\n" + "=" * 60)
        print("STELLAR SYSTEM STATISTICS SUMMARY")
        print("=" * 60)
        
        total_rolls = sum(self.stat_counter.values())
        print(f"Total Rolls: {total_rolls}")
        print()

        if self.stat_counter:
            # Sort by count (descending)
            sorted_stats = sorted(self.stat_counter.items(), key=lambda x: x[1], reverse=True)
            
            print("DETECTED STATS:")
            print("-" * 60)
            for stat_key, count in sorted_stats:
                # Clean noisy OCR tokens while keeping the stat name/value
                clean_stat = stat_key.replace("»", " ")
                clean_stat = re.sub(r'stellarforce', '', clean_stat, flags=re.IGNORECASE)
                clean_stat = re.sub(r'stellar', '', clean_stat, flags=re.IGNORECASE)
                clean_stat = re.sub(r'\s+', ' ', clean_stat).strip()
                if not clean_stat:
                    clean_stat = stat_key  # fallback to original if cleaning removed everything
                percentage = (count / total_rolls * 100) if total_rolls > 0 else 0
                print(f"  {clean_stat:40s} × {count:3d} ({percentage:5.1f}%)")
            print()
        
        print("=" * 60)
