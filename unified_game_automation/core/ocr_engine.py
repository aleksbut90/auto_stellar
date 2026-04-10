import pytesseract
import re
import os
import sys
import cv2
import numpy as np
from PIL import Image


class OCREngine:
    def __init__(self, status_callback=None):
        self.status_callback = status_callback

        # путь к tesseract.exe
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
        if self.status_callback:
            self.status_callback(message)

    # ---------------------------------------------------------
    # ОСНОВНОЙ OCR
    # ---------------------------------------------------------
    def extract_text(self, image):
        try:
            if image is None:
                return ""

            img = np.array(image)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            # --- ПРОХОД №1 (обычный) ---
            _, thresh = cv2.threshold(
                gray, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            text1 = pytesseract.image_to_string(
                Image.fromarray(thresh),
                lang="rus+eng",
                config="--oem 3 --psm 6"
            )
            text1 = self._fix_cyrillic_text(text1)

            # Если слово после "Связь" есть — возвращаем
            if re.search(r"связь\s+\w+", text1.lower()):
                return text1

            # --- ПРОХОД №2 (усиленный, только для слабого слова) ---
            # Усиливаем контраст
            enhanced = cv2.equalizeHist(gray)

            # Инверсия
            enhanced = cv2.bitwise_not(enhanced)

            # Морфология — расширяем тонкие буквы
            kernel = np.ones((2, 2), np.uint8)
            enhanced = cv2.dilate(enhanced, kernel, iterations=1)

            # OCR одной строки
            text2 = pytesseract.image_to_string(
                Image.fromarray(enhanced),
                lang="rus+eng",
                config="--oem 3 --psm 7"
            )
            text2 = self._fix_cyrillic_text(text2)

            # Вставляем найденное слово
            if text2:
                return text1.replace("связь", f"связь {text2}")

            return text1

        except Exception as e:
            self.update_status(f"OCR error: {str(e)}")
            return ""


    # ---------------------------------------------------------
    # ФИКС ЛАТИНИЦЫ → КИРИЛЛИЦА + исправления под твои логи
    # ---------------------------------------------------------
    def _fix_cyrillic_text(self, text):
        if not text:
            return ""

        # -----------------------------
        # 1. Латиница → Кириллица
        # -----------------------------
        latin_to_cyr = {
            'A': 'А', 'a': 'а',
            'B': 'В', 'b': 'в',
            'E': 'Е', 'e': 'е',
            'K': 'К', 'k': 'к',
            'M': 'М', 'm': 'м',
            'H': 'Н', 'h': 'н',
            'O': 'О', 'o': 'о',
            'P': 'Р', 'p': 'р',
            'C': 'С', 'c': 'с',
            'T': 'Т', 't': 'т',
            'X': 'Х', 'x': 'х',
            'Y': 'У', 'y': 'у',
            'Z': 'З', 'z': 'з',

            # OCR-ошибки
            'R': 'Г', 'r': 'г',
            'N': 'П', 'n': 'п',
            'G': 'Д', 'g': 'д',
            'S': 'С', 's': 'с',
            'V': 'У', 'v': 'у',
            'F': 'Ф', 'f': 'ф',
            'L': 'Л', 'l': 'л',
            'D': 'Д', 'd': 'д',
            'U': 'И', 'u': 'и',
            'J': 'Й', 'j': 'й',
            'Q': 'К', 'q': 'к',
            'W': 'Ш', 'w': 'ш',
        }

        fixed = ""
        for ch in text:
            fixed += latin_to_cyr.get(ch, ch)

        fixed = fixed.lower()

        # -----------------------------
        # 2. Фиксы PvE (все варианты)
        # -----------------------------
        pve_variants = [
            "руе", "pve", "рве", "rve", "pye", "pue", "pве",
            "pуе", "руe", "руё", "pуе", "pye", "pye"
        ]
        for v in pve_variants:
            fixed = fixed.replace(v, "pve")

        # -----------------------------
        # 3. Фиксы слова «Горе»
        # -----------------------------
        gore_variants = [
            "торе", "tоре", "тope", "гope", "гope", "гope",
            "тope", "тope", "тope", "гope", "гope", "гope"
        ]
        for v in gore_variants:
            fixed = fixed.replace(v, "горе")

        # -----------------------------
        # 4. Фиксы слова «Гнев»
        # -----------------------------
        fixed = fixed.replace("meg", "гнев")
        fixed = fixed.replace("mег", "гнев")
        fixed = fixed.replace("мег", "гнев")
        fixed = fixed.replace("гневв", "гнев")

        # -----------------------------
        # 5. Фиксы слова «Тоска»
        # -----------------------------
        fixed = fixed.replace("тосrа", "тоска")
        fixed = fixed.replace("тосkа", "тоска")
        fixed = fixed.replace("тосcа", "тоска")
        fixed = fixed.replace("тосrка", "тоска")

        # -----------------------------
        # 6. Фиксы слова «Пустота»
        # -----------------------------
        fixed = fixed.replace("пустоtа", "пустота")
        fixed = fixed.replace("пустоta", "пустота")
        fixed = fixed.replace("пустотаа", "пустота")

        # -----------------------------
        # 7. Фиксы слова «Забвение»
        # -----------------------------
        fixed = fixed.replace("забвeние", "забвение")
        fixed = fixed.replace("забвениее", "забвение")
        fixed = fixed.replace("забвeнie", "забвение")

        # -----------------------------
        # 8. Фиксы «уворота»
        # -----------------------------
        fixed = fixed.replace("увороta", "уворота")
        fixed = fixed.replace("увороtа", "уворота")
        fixed = fixed.replace("увороt", "уворота")

        # -----------------------------
        # 9. Фиксы «игнор»
        # -----------------------------
        fixed = fixed.replace("игнoр", "игнор")
        fixed = fixed.replace("игнoр", "игнор")
        fixed = fixed.replace("игнорр", "игнор")

        # -----------------------------
        # 10. Фиксы «звезда / звёздная сила»
        # -----------------------------
        fixed = fixed.replace("звесдная", "звёздная")
        fixed = fixed.replace("звесднал", "звёздная")
        fixed = fixed.replace("звезвыр", "звёздный")
        fixed = fixed.replace("звезд р", "звезда")
        fixed = fixed.replace("звездаа", "звезда")

        # -----------------------------
        # 11. Удаление мусора
        # -----------------------------
        fixed = re.sub(r"[^\w\s+ёЁа-яА-Я]", " ", fixed)
        fixed = re.sub(r"\s+", " ", fixed).strip()

        return fixed

    # ---------------------------------------------------------
    # ПАРСИНГ СТАТА (минимальный, не ломает кириллицу)
    # ---------------------------------------------------------
    def parse_stellar_text(self, text):
        if not text:
            return ""
        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip().lower()
