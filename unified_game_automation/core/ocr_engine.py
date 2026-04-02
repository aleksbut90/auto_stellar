# Tesseract OCR engine wrapper
# Replaces PaddleOCR functionality from arrival_skill_ocr

import pytesseract
import re
import os
import sys

class OCREngine:
    def __init__(self, status_callback=None):
        """Initialize the Tesseract OCR engine"""
        self.status_callback = status_callback

        # Set up Tesseract path (exactly as in main.py)
        # The base_path should be the main script directory, not the core module directory
        import __main__
        if hasattr(__main__, '__file__'):
            main_script_dir = os.path.dirname(os.path.abspath(__main__.__file__))
        else:
            main_script_dir = os.getcwd()

        base_path = getattr(sys, "_MEIPASS", main_script_dir)
        tesseract_path = os.path.join(base_path, "Tesseract", "tesseract.exe")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        if status_callback:
            status_callback("Tesseract OCR initialized")

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def extract_text(self, image):
        """
        Extract text from image using Tesseract
        Args:
            image: PIL Image object
        Returns:
            Raw text string from OCR
        """
        try:
            if image is None:
                return ""

            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            self.update_status(f"OCR error: {str(e)}")
            return ""

    def parse_stellar_text(self, text):
        """
        Parse text for stellar system format
        Expected format: "Stellar" and "Stellar Force" with option name and value
        """
        # Clean up text (same as main.py)
        text = re.sub(r"\s+", "", text).lower()
        text = re.sub(r'([A-Za-z]+)4(\d)', r'\1+\2', text)

        if "stellarforce4" in text:
            text = text.replace("stellarforce4", "stellarforce+")

        return text

    def find_numbers(self, text):
        """Find all numbers in text"""
        return re.findall(r"\d+", text)

    def clean_price_text(self, text):
        """
        Clean OCR text for price detection
        Removes dots, spaces, commas, and ALL letters - keep only numbers
        """
        # Remove all dots, spaces, commas, and letters - keep only numbers
        cleaned = re.sub(r'[.,\s]', '', text)  # Remove dots, spaces, commas
        cleaned = re.sub(r'[a-zA-Z]', '', cleaned)  # Remove all letters

        return cleaned

    def extract_prices(self, text):
        """
        Extract min price and weekly average price from OCR text
        Layout: Weekly average on top, min price below
        Returns:
            dict with 'min_price' and 'weekly_avg' keys, or None if not found
        """
        try:
            # Split text into lines to handle top/bottom layout
            lines = text.strip().split('\n')

            # Clean each line and extract numbers
            numbers = []
            for line in lines:
                cleaned_line = self.clean_price_text(line)
                # Find all numbers in this line
                line_numbers = re.findall(r'\d+', cleaned_line)
                numbers.extend(line_numbers)

            if len(numbers) >= 2:
                # We have at least 2 numbers (could be same or different)
                # First number is weekly average (top), second is min price (bottom)
                return {
                    'weekly_avg': numbers[0],
                    'min_price': numbers[1],
                    'raw_text': text,
                    'cleaned_text': ' '.join(numbers[:2]),
                    'all_numbers': numbers
                }
            elif len(numbers) == 1:
                # Only one number found - set both weekly_avg and min_price to same value
                return {
                    'weekly_avg': numbers[0],
                    'min_price': numbers[0],
                    'raw_text': text,
                    'cleaned_text': numbers[0],
                    'all_numbers': numbers
                }
            else:
                return None

        except Exception as e:
            self.update_status(f"Price extraction error: {str(e)}")
            return None
