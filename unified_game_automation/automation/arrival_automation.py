# Arrival skill automation logic
# Ported from arrival_skill_ocr/automation.py

import time
import threading
import re
from tkinter import messagebox
from data.arrival_data import get_offensive_skills, get_defensive_skills, get_base_stat_name
from automation.base_automation import BaseAutomation

class ArrivalAutomation(BaseAutomation):
    def __init__(self, game_connector, ocr_engine, status_callback=None):
        """Initialize arrival skill automation"""
        super().__init__(game_connector, ocr_engine, status_callback)

        # Automation state
        self.apply_button_coords = None
        self.change_button_coords = None
        self.detection_region = None

        # Configuration
        self.area = None
        self.grade_area = None

        # Stat tracking
        self.stat_counter = {}
        self.unmapped_ocr_counter = {}

    def set_area(self, area):
        """Set the OCR area"""
        self.area = area
        self.detection_region = area

    def set_grade_area(self, area):
        """Set the OCR area for grade detection"""
        self.grade_area = area

    def set_apply_button(self, coords):
        """Set the apply button coordinates"""
        self.apply_button_coords = coords

    def set_change_button(self, coords):
        """Set the change button coordinates"""
        self.change_button_coords = coords

    def start(self, desired_stats=None, logic_mode="OR"):
        """Start the arrival automation"""
        # Check if button coordinates are set
        if not self.apply_button_coords or not self.change_button_coords:
            messagebox.showerror("Error", "Please set both Apply and Change button coordinates.")
            return False

        if not self.area:
            messagebox.showwarning("Missing area definition", "Fix area definition first!")
            return False

        # If any desired stat requires grade checking, ensure grade area is set
        if desired_stats:
            def has_grade(entries):
                return any((len(entry) >= 3 and entry[2].get("mode") == "grade") for entry in (entries or []))

            grade_needed = has_grade(desired_stats.get('offensive')) or has_grade(desired_stats.get('defensive'))
            if grade_needed and not self.grade_area:
                messagebox.showwarning("Missing grade OCR area", "Please set the Grade OCR area before starting.")
                return False

        # Connect to game if not already connected
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return False

        # Reset counters for new run
        self.stat_counter = {}
        self.unmapped_ocr_counter = {}

        self.update_status("Starting arrival skill automation")

        self.running = True
        self.logic_mode = logic_mode  # Store logic mode (OR or AND)

        # Start automation in thread
        threading.Thread(target=self.reroll_loop, args=(desired_stats,), daemon=True).start()
        return True

    def stop(self):
        """Stop the arrival automation"""
        self.running = False
        self.update_status("Arrival automation stopped")

        # Show summary of stats in console/terminal if we have any
        if self.stat_counter:
            self.show_stats_summary()

    def detect_text_in_image(self, image):
        """Detect text in image using Tesseract and parse for arrival skill format"""
        if image is None:
            return {}, {}, []

        # Extract text using Tesseract
        raw_text = self.ocr_engine.extract_text(image)

        # Fix OCR misreading + as 4 (only when there's no + sign already)
        import re
        cleaned_text = re.sub(r'([A-Za-z\s\.]+)\s4(\d)', r'\1 +\2', raw_text)

        # Fix OCR misreading dots as commas
        cleaned_text = cleaned_text.replace(',', '.')

        # Store raw OCR lines for custom stat matching
        raw_lines = [line.strip() for line in cleaned_text.strip().split('\n') if line.strip()]
        
        # Parse for arrival skill format (dual stats, no "Stellar" text)
        current_stats, line_positions = self.parse_arrival_text(cleaned_text)
        
        return current_stats, line_positions, raw_lines

    def parse_arrival_text(self, text):
        """
        Parse text for arrival skill format
        Expected format: Two stats with values (no "Stellar" text)
        Example:
        Add. Damage        +45
        HP Absorb Up       +2%

        Special handling for long arrival skill names that get cut off:
        - "Arrival Skill Cool time decreas," -> "Arrival Skill Cool Time decreased."
        - "Arrival Skill Duration" -> "Arrival Skill Duration Increase"
        
        Returns: (stats_dict, line_positions_dict)
        - stats_dict: {stat_name: value}
        - line_positions_dict: {stat_name: line_index} where 0 = first line (offensive), 1 = second line (defensive)
        """
        import re

        current_stats = {}
        line_positions = {}  # Track which line each stat came from

        # First, handle special cases for arrival skills with truncated names
        special_stats = self.handle_arrival_skill_special_cases(text)
        current_stats.update(special_stats)
        # Special cases are typically on first line, but we'll mark them as line 0
        for stat in special_stats:
            line_positions[stat] = 0

        # Split text into lines for normal processing
        lines = text.strip().split('\n')
        
        # Track which line index we're on (for non-empty lines only)
        line_index = 0

        # Look for stat patterns in each line
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip lines that are already handled by special cases
            if self.is_arrival_skill_line(line):
                continue

            # Try to match stat patterns: "Stat Name +Value" or "Stat Name Value"
            # Handle both percentage and numeric values
            patterns = [
                r'(.+?)\s*\+(\d+)%',  # "Stat Name +5%"
                r'(.+?)\s*\+(\d+)',   # "Stat Name +45"
                r'(.+?)\s*(\d+)%',    # "Stat Name 5%"
                r'(.+?)\s*(\d+)',     # "Stat Name 45"
            ]

            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    stat_name = match.group(1).strip()
                    value_str = match.group(2).strip()

                    # Clean up stat name
                    stat_name = stat_name.replace('.', '').strip()

                    # Try to match against known stats
                    matched_stat = self.match_stat_name(stat_name)
                    if matched_stat:
                        try:
                            value = int(value_str)
                            current_stats[matched_stat] = value
                            line_positions[matched_stat] = line_index  # Track which line this stat is on
                        except ValueError:
                            continue
                    else:
                        # Track unmapped stats for summary
                        if '%' in pattern:
                            value_str += '%'
                        unmapped_key = f"{stat_name} +{value_str}"
                        self.unmapped_ocr_counter[unmapped_key] = self.unmapped_ocr_counter.get(unmapped_key, 0) + 1
                    break
            
            # Increment line index for next non-empty line
            line_index += 1

        return current_stats, line_positions

    def detect_grade(self):
        """Detect roll grade using OCR on the configured grade area"""
        if not self.grade_area:
            return None

        # Capture grade area
        screenshot = self.game_connector.capture_area_bitblt(self.grade_area)
        if screenshot is None:
            return None

        text = self.ocr_engine.extract_text(screenshot)
        if not text:
            return None

        import re
        text_lower = text.lower()

        # Special case: OCR often misreads "1" as "I" or "l"
        # Check for "ist grade", "irst grade", "lst grade" etc. (misread "1st")
        if re.search(r'\b(?:i|1|l)[st]\s+grade', text_lower) or 'ist grade' in text_lower:
            return 1

        # Look for patterns like "1st grade", "2nd grade", etc.
        match = re.search(r'(\d+)\s*(?:st|nd|rd|th)?\s*grade', text_lower)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

        # Fallback: look for any number in the text
        numbers = re.findall(r'\d+', text_lower)
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                pass

        # Final fallback: if text contains "grade" but no number detected, it's likely OCR misreading
        # Check for common misreadings of "1st", "2nd", "3rd", etc.
        if 'grade' in text_lower:
            # Check for "ist" (1st misread), "2nd", "3rd", "4th", "5th", "6th" patterns
            if re.search(r'\b(?:i|l)[st]', text_lower) or 'ist' in text_lower:
                return 1
            elif '2nd' in text_lower or 'second' in text_lower:
                return 2
            elif '3rd' in text_lower or 'third' in text_lower:
                return 3
            elif '4th' in text_lower or 'fourth' in text_lower:
                return 4
            elif '5th' in text_lower or 'fifth' in text_lower:
                return 5
            elif '6th' in text_lower or 'sixth' in text_lower:
                return 6

        return None

    def handle_arrival_skill_special_cases(self, text):
        """
        Handle special cases for arrival skills with long names that get truncated
        Returns a dictionary of detected arrival skills without values
        """
        special_stats = {}
        text_lower = text.lower()

        # Case 1: Arrival Skill Cool Time decreased
        if ('arrival' in text_lower and 'cool' in text_lower and 'time' in text_lower) or \
           ('arrival skill cool time decreas' in text_lower):
            special_stats["Arrival Skill Cool Time decreased."] = None

        # Case 2: Arrival Skill Duration Increase
        elif ('arrival' in text_lower and 'duration' in text_lower) or \
             ('arrival skill duration' in text_lower):
            special_stats["Arrival Skill Duration Increase"] = None

        return special_stats

    def is_arrival_skill_line(self, line):
        """
        Check if a line contains arrival skill text that should be skipped in normal processing
        """
        line_lower = line.lower()
        return ('arrival' in line_lower and ('cool' in line_lower or 'duration' in line_lower))

    def match_stat_name(self, detected_name):
        """Match detected stat name to known arrival skill stats"""
        from data.arrival_data import get_all_base_stat_names

        detected_lower = detected_name.lower().replace(' ', '').replace('.', '')

        # Try exact matches first
        for known_stat in get_all_base_stat_names():
            known_lower = known_stat.lower().replace(' ', '').replace('.', '')
            if detected_lower == known_lower:
                return known_stat

        # Try partial matches
        for known_stat in get_all_base_stat_names():
            known_lower = known_stat.lower().replace(' ', '').replace('.', '')
            if detected_lower in known_lower or known_lower in detected_lower:
                return known_stat

        return None

    def reroll_loop(self, desired_stats):
        """Main reroll loop for arrival skill automation"""
        self.update_status("▶️ Starting arrival skill automation...")

        iteration_count = 0

        # Pre-compute stat categories
        offensive_base_stats = set(get_base_stat_name(stat) for stat in get_offensive_skills())
        defensive_base_stats = set(get_base_stat_name(stat) for stat in get_defensive_skills())

        # First click the Change button to remove current option
        self.game_connector.click_at_position(self.change_button_coords)
        time.sleep(0.4)

        while self.running:
            iteration_count += 1

            # Click Apply button to apply a new option
            self.game_connector.click_at_position(self.apply_button_coords)
            time.sleep(0.5)  # Wait for game to update

            # Capture screenshot using BitBlt
            screenshot = self.game_connector.capture_area_bitblt(self.area)
            if screenshot is None:
                self.update_status("Failed to capture screen, retrying...")
                time.sleep(0.5)
                continue

            # Detect text in the screenshot
            current_stats, line_positions, raw_ocr_lines = self.detect_text_in_image(screenshot)

            # Detect grade if configured
            current_grade = self.detect_grade()

            if current_stats:
                # Track stats for summary
                for stat, value in current_stats.items():
                    # For grade-based stats (value is None), use the detected grade
                    if value is None and stat == "Arrival Skill Cool Time decreased.":
                        # Always try to detect grade for this stat when tracking
                        # Use current_grade if available, otherwise try to detect it now
                        grade_to_use = current_grade if current_grade is not None else self.detect_grade()
                        if grade_to_use is not None:
                            stat_key = f"{stat} +Grade {grade_to_use}"
                        else:
                            stat_key = f"{stat} +None"
                    elif value is None:
                        stat_key = f"{stat} +None"
                    else:
                        stat_key = f"{stat} +{value}"
                    self.stat_counter[stat_key] = self.stat_counter.get(stat_key, 0) + 1

                # Log detected stats
                stat_list = [f"{stat}: {value}" for stat, value in current_stats.items()]
                if stat_list:
                    self.update_status(f"Roll #{iteration_count}: " + " | ".join(stat_list))
            else:
                self.update_status(f"Roll #{iteration_count}: No stats detected")

            # Check if we have desired stats
            if self.check_desired_stats(current_stats, desired_stats, current_grade, line_positions, raw_ocr_lines):
                self.update_status("🎉🎉🎉 SUCCESS! DESIRED STATS FOUND! 🎉🎉🎉")
                self.stop()
                messagebox.showinfo("Success", "Desired stats found! Automation stopped.")
                # Statistics summary will be shown in console/terminal via show_stats_summary() in stop()
                break

            # If desired stats not found, click the Change button to reroll
            self.game_connector.click_at_position(self.change_button_coords)
            time.sleep(0.4)

    def check_desired_stats(self, current_stats, desired_stats, current_grade=None, line_positions=None, raw_ocr_lines=None):
        """
        Check if current stats meet the desired criteria for arrival skills
        - OR logic within each category: ANY offensive stat OR ANY defensive stat can match
        - AND logic between categories: If both categories have stats, at least one from EACH must be found
        - Line 0 (first line) = offensive stat, Line 1 (second line) = defensive stat
        """
        if not desired_stats:
            return True

        if not desired_stats.get('offensive') and not desired_stats.get('defensive'):
            return True

        if line_positions is None:
            line_positions = {}
        if raw_ocr_lines is None:
            raw_ocr_lines = []

        # Helper function to normalize text for custom stat matching
        def normalize_for_matching(text):
            """Remove dots, make lowercase, remove + and numbers"""
            # Remove + and numbers
            text = re.sub(r'[+\d]', '', text)
            # Remove dots, make lowercase
            return text.lower().replace('.', '').strip()

        # Check if any offensive stat matches (OR logic within offensive category)
        # Offensive stats must be on line 0 (first line)
        off_match = False
        matched_offensive = None
        if desired_stats.get('offensive'):
            # Get the offensive line (line 0) for custom stat matching
            offensive_line_text = raw_ocr_lines[0] if len(raw_ocr_lines) > 0 else ""
            offensive_line_normalized = normalize_for_matching(offensive_line_text)
            
            for entry in desired_stats['offensive']:
                # Entry format: (display_stat_name, min_value, meta)
                display_stat_name, min_value = entry[0], entry[1]
                meta = entry[2] if len(entry) >= 3 else {}
                base_stat_name = get_base_stat_name(display_stat_name)

                # Check if this is a custom stat (not in known stats)
                from data.arrival_data import get_all_base_stat_names
                is_custom_stat = base_stat_name not in get_all_base_stat_names()

                stat_value = None
                matched_stat_key = None
                
                if is_custom_stat:
                    # Custom stat: simple substring match in normalized OCR line
                    custom_stat_normalized = normalize_for_matching(base_stat_name)
                    if custom_stat_normalized in offensive_line_normalized:
                        # Extract value from the line
                        numbers = re.findall(r'\d+', offensive_line_text)
                        if numbers:
                            stat_value = int(numbers[0])
                        else:
                            stat_value = 0  # Found the stat but no value
                        matched_stat_key = base_stat_name
                else:
                    # Known stat: check in current_stats on line 0
                    if base_stat_name in current_stats:
                        # Verify it's on line 0 (offensive line)
                        if base_stat_name in line_positions and line_positions[base_stat_name] == 0:
                            stat_value = current_stats[base_stat_name]
                            matched_stat_key = base_stat_name
                    else:
                        # Check for partial match (e.g., "Add" should match "Add. Damage")
                        base_stat_lower = base_stat_name.lower().replace(' ', '').replace('.', '')
                        for stat_key in current_stats.keys():
                            # Only check stats on line 0 (offensive line)
                            if stat_key not in line_positions or line_positions[stat_key] != 0:
                                continue
                            stat_key_lower = stat_key.lower().replace(' ', '').replace('.', '')
                            if base_stat_lower in stat_key_lower:
                                stat_value = current_stats[stat_key]
                                matched_stat_key = stat_key
                                break
                        
                        # If still not found, try substring match in raw OCR line (fallback for parsing failures)
                        if stat_value is None:
                            base_stat_normalized = normalize_for_matching(base_stat_name)
                            if base_stat_normalized in offensive_line_normalized:
                                # Extract value from the line
                                numbers = re.findall(r'\d+', offensive_line_text)
                                if numbers:
                                    stat_value = int(numbers[0])
                                else:
                                    stat_value = 0
                                matched_stat_key = base_stat_name

                # Check if stat was found (stat_value may be None for special cases)
                if stat_value is not None or (stat_value is None and matched_stat_key is not None):
                    # Grade-based detection (works even if stat_value is None for special cases)
                    if meta.get("mode") == "grade":
                        if current_grade is None:
                            self.update_status("Grade not detected yet")
                            continue
                        if current_grade >= min_value:
                            off_match = True
                            matched_offensive = display_stat_name
                            self.update_status(f"✅ MATCH: {display_stat_name} with Grade {current_grade} (target: ≥{min_value})")
                            break
                    else:
                        # Value-based detection (requires stat_value to be not None)
                        if stat_value is None:
                            # Special case: arrival skill detected but value unavailable due to UI collision
                            self.update_status(f"🎉 FOUND: {display_stat_name} detected!")
                            self.update_status(f"⚠️ Note: Cannot verify value due to UI collision - please check manually")
                            self.stop()
                            # Info popup removed - status already shows the information
                            return True
                        elif stat_value >= min_value:
                            off_match = True
                            matched_offensive = display_stat_name
                            self.update_status(f"✅ MATCH: Found {display_stat_name} with value {stat_value} (target: {min_value}+)")
                            break  # Found a match, no need to check other offensive stats
        
        # Track whether we're checking offensive stats
        has_offensive_requirements = bool(desired_stats.get('offensive'))

        # Check if any defensive stat matches (OR logic within defensive category)
        # Defensive stats must be on line 1 (second line)
        def_match = False
        matched_defensive = None
        if desired_stats.get('defensive'):
            # Get the defensive line (line 1) for custom stat matching
            defensive_line_text = raw_ocr_lines[1] if len(raw_ocr_lines) > 1 else ""
            defensive_line_normalized = normalize_for_matching(defensive_line_text)
            
            for entry in desired_stats['defensive']:
                display_stat_name, min_value = entry[0], entry[1]
                meta = entry[2] if len(entry) >= 3 else {}
                base_stat_name = get_base_stat_name(display_stat_name)

                # Check if this is a custom stat (not in known stats)
                from data.arrival_data import get_all_base_stat_names
                is_custom_stat = base_stat_name not in get_all_base_stat_names()

                stat_value = None
                matched_stat_key = None
                
                if is_custom_stat:
                    # Custom stat: simple substring match in normalized OCR line
                    custom_stat_normalized = normalize_for_matching(base_stat_name)
                    if custom_stat_normalized in defensive_line_normalized:
                        # Extract value from the line
                        numbers = re.findall(r'\d+', defensive_line_text)
                        if numbers:
                            stat_value = int(numbers[0])
                        else:
                            stat_value = 0  # Found the stat but no value
                        matched_stat_key = base_stat_name
                else:
                    # Known stat: check in current_stats on line 1
                    if base_stat_name in current_stats:
                        # Verify it's on line 1 (defensive line)
                        if base_stat_name in line_positions and line_positions[base_stat_name] == 1:
                            stat_value = current_stats[base_stat_name]
                            matched_stat_key = base_stat_name
                    else:
                        # Check for partial match (e.g., "Ignore" should match "Ignore Evasion")
                        base_stat_lower = base_stat_name.lower().replace(' ', '').replace('.', '')
                        for stat_key in current_stats.keys():
                            # Only check stats on line 1 (defensive line)
                            if stat_key not in line_positions or line_positions[stat_key] != 1:
                                continue
                            stat_key_lower = stat_key.lower().replace(' ', '').replace('.', '')
                            if base_stat_lower in stat_key_lower:
                                stat_value = current_stats[stat_key]
                                matched_stat_key = stat_key
                                break
                        
                        # If still not found, try substring match in raw OCR line (fallback for parsing failures)
                        if stat_value is None:
                            base_stat_normalized = normalize_for_matching(base_stat_name)
                            if base_stat_normalized in defensive_line_normalized:
                                # Extract value from the line
                                numbers = re.findall(r'\d+', defensive_line_text)
                                if numbers:
                                    stat_value = int(numbers[0])
                                else:
                                    stat_value = 0
                                matched_stat_key = base_stat_name

                if stat_value is not None:
                    if meta.get("mode") == "grade":
                        if current_grade is None:
                            self.update_status("Grade not detected yet")
                            continue
                        if current_grade >= min_value:
                            def_match = True
                            matched_defensive = display_stat_name
                            self.update_status(f"✅ MATCH: {display_stat_name} with Grade {current_grade} (target: ≥{min_value})")
                            break
                    else:
                        if stat_value is None:
                            # Special case: arrival skill detected but value unavailable due to UI collision
                            self.update_status(f"🎉 FOUND: {display_stat_name} detected!")
                            self.update_status(f"⚠️ Note: Cannot verify value due to UI collision - please check manually")
                            self.stop()
                            # Info popup removed - status already shows the information
                            return True
                        elif stat_value >= min_value:
                            def_match = True
                            matched_defensive = display_stat_name
                            self.update_status(f"✅ MATCH: Found {display_stat_name} with value {stat_value} (target: {min_value}+)")
                            break  # Found a match, no need to check other defensive stats
        
        # Track whether we're checking defensive stats
        has_defensive_requirements = bool(desired_stats.get('defensive'))

        # Final check: Use OR or AND logic between categories based on setting
        logic_mode = getattr(self, 'logic_mode', 'OR')  # Default to OR if not set
        
        # Determine result based on which categories have requirements
        if has_offensive_requirements and has_defensive_requirements:
            # Both categories have requirements - use logic_mode
            if logic_mode == "AND":
                # AND logic: Both categories must match
                result = off_match and def_match
            else:
                # OR logic: Either category can match
                result = off_match or def_match
        elif has_offensive_requirements:
            # Only offensive stats required - only check offensive match
            result = off_match
        elif has_defensive_requirements:
            # Only defensive stats required - only check defensive match
            result = def_match
        else:
            # No requirements (shouldn't happen, but handle it)
            result = True
        
        return result

    def show_stats_summary(self):
        """Show summary of detected stats in console/terminal"""
        print("\n" + "=" * 60)
        print("ARRIVAL SKILL STATISTICS SUMMARY")
        print("=" * 60)
        
        total_rolls = sum(self.stat_counter.values())
        print(f"Total Rolls: {total_rolls}")
        print()

        # Separate stats by category
        offensive_base_stats = set(get_base_stat_name(stat) for stat in get_offensive_skills())
        defensive_base_stats = set(get_base_stat_name(stat) for stat in get_defensive_skills())

        # Group stats by category
        offensive_stats = {}
        defensive_stats = {}
        other_stats = {}

        for stat_key, count in self.stat_counter.items():
            # Extract the stat name from the key (format is "stat_name +value")
            parts = stat_key.split("+")
            if len(parts) >= 1:
                stat_name = parts[0].strip()

                # Categorize the stat
                if stat_name in offensive_base_stats:
                    offensive_stats[stat_key] = count
                elif stat_name in defensive_base_stats:
                    defensive_stats[stat_key] = count
                else:
                    other_stats[stat_key] = count

        total_rolls = sum(self.stat_counter.values())
        
        # Display offensive stats
        if offensive_stats:
            print("OFFENSIVE STATS:")
            print("-" * 60)
            for stat_key, count in sorted(offensive_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_rolls * 100) if total_rolls > 0 else 0
                print(f"  {stat_key:40s} × {count:3d} ({percentage:5.1f}%)")
            print()

        # Display defensive stats
        if defensive_stats:
            print("DEFENSIVE STATS:")
            print("-" * 60)
            for stat_key, count in sorted(defensive_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_rolls * 100) if total_rolls > 0 else 0
                print(f"  {stat_key:40s} × {count:3d} ({percentage:5.1f}%)")
            print()

        # Merge unmapped stats into other_stats
        for stat_key, count in self.unmapped_ocr_counter.items():
            other_stats[stat_key] = other_stats.get(stat_key, 0) + count

        # Display other stats (includes unmapped stats)
        if other_stats:
            print("OTHER STATS:")
            print("-" * 60)
            for stat_key, count in sorted(other_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_rolls * 100) if total_rolls > 0 else 0
                print(f"  {stat_key:40s} × {count:3d} ({percentage:5.1f}%)")
            print()

        print("=" * 60)
        print()

        # Reset counters for next run
        self.stat_counter = {}
        self.unmapped_ocr_counter = {}
