# Stellar system automation logic
# Extracted from main.py

import time
import re
import threading
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

    def _start_automation_loop(self):
        """Start the automation loop with initial delay"""
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
            # Wait for visual effects to appear, then click to close them
            time.sleep(self.effect_delay_ms / 1000.0)

            # Click imprint button (which becomes "close" button) to clear visual effects
            if not self.game_connector.click_at_position(self.imprint_button_coords):
                self.update_status("Click failed")

            # Small delay to let effects clear
            time.sleep(0.2)

            # Capture screenshot using BitBlt
            screenshot = self.game_connector.capture_area_bitblt(self.area)
            if screenshot is None:
                self.update_status("Capture failed")
                self.stop()
                return

            # Extract text using Tesseract
            raw_text = self.ocr_engine.extract_text(screenshot)

            text = self.ocr_engine.parse_stellar_text(raw_text)
            
            self.iteration_count += 1

            # Check for exactly one number (stellar format validation)
            numbers_found = self.ocr_engine.find_numbers(text)

            if len(numbers_found) != 1:
                self.wrong_read_counter += 1
                if self.wrong_read_counter > 5:
                    self.update_status("Wrong number count - check area definition")
                    self.stop()
                    self.loop_in_progress = False
                    return
                else:
                    self.update_status(f"OCR read error (attempt {self.wrong_read_counter}/5): found {len(numbers_found)} numbers")
                    self.loop_in_progress = False
                    # Schedule next attempt with longer delay
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
            
            if self.stat_config:
                for stat_name, min_value in self.stat_config.items():
                    # Check if stat name is in text
                    if stat_name in text:
                        # Special handling for penetration exceptions
                        if stat_name == "penetration":
                            exceptions = get_penetration_exceptions()
                            if any(exc in text for exc in exceptions):
                                self.update_status("Ignoring penetration exception")
                                continue
                        
                        # Check minimum value for this specific stat
                        value_matches = True
                        if min_value:
                            if min_value.isdigit():
                                min_val_int = int(min_value)
                                value_matches = self.numeric_compare(min_val_int, text)
                            else:
                                value_matches = (min_value in text)
                        
                        # If both stat name and value match (or no value required), we found it!
                        if value_matches:
                            found_match = True
                            matched_stat = stat_name
                            # Extract the actual value from text for display
                            matched_value = stat_value_detected if stat_value_detected else "N/A"
                            break

            # Check success conditions
            if found_match:
                min_val_display = self.stat_config.get(matched_stat, "")
                if min_val_display:
                    self.update_status(f"Found: {matched_stat} {matched_value} (≥{min_val_display})")
                else:
                    self.update_status(f"Found: {matched_stat} {matched_value}")
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
                # Continue automation - click imprint button
                if not self.game_connector.is_connected():
                    if not self.game_connector.connect_to_game():
                        self.update_status("Connection failed")
                        self.stop()
                        return

                # Double click with delay (as in original)
                if not self.game_connector.click_at_position(self.imprint_button_coords):
                    self.update_status("Click failed")

                time.sleep(0.3)

                if not self.game_connector.click_at_position(self.imprint_button_coords):
                    self.update_status("Click failed")

                self.loop_in_progress = False
                # Schedule next iteration
                threading.Timer(self.delay_ms / 1000, self.loop_ocr).start()
                return

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
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
