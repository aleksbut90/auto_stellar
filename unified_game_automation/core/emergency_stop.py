"""
Emergency Stop Handler - надежная остановка бота на уровне Windows API
Работает даже когда бот контролирует ввод через pydirectinput

Механизм работы:
1. Низкоуровневый хук клавиатуры Windows API (перехватывает ESC до приложений)
2. Файл-флаг .bot_stop_flag (дублирующий механизм)
3. Очистка буфера ввода
"""

import threading
import os
import time
import ctypes
from ctypes import wintypes

# Windows API константы
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100

# Глобальные переменные
_low_level_hook = None
_stop_callback = None
_hook_thread = None
_running = False

# Путь к файлу-флагу
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STOP_FLAG_FILE = os.path.join(PROJECT_ROOT, ".bot_stop_flag")

# Счётчик вызовов для отладки
_stop_flag_check_count = 0


class KBDLLHOOKSTRUCT(ctypes.Structure):
    """Структура для низкоуровневого хука клавиатуры"""
    _fields_ = [
        ('vkCode', wintypes.DWORD),
        ('scanCode', wintypes.DWORD),
        ('flags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]


# Типы callback функций
HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_int,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM
)


def _low_level_keyboard_handler(nCode, wParam, lParam):
    """Обработчик низкоуровневых событий клавиатуры"""
    global _stop_callback

    if nCode >= 0 and wParam == WM_KEYDOWN:
        kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk_code = kb_struct.vkCode

        # VK_ESCAPE = 0x1B
        if vk_code == 0x1B:  # ESC
            print("🚨 [EMERGENCY_STOP] Обнаружено нажатие ESC на низком уровне!")
            
            # Вызываем callback (он сам установит флаг)
            if _stop_callback:
                try:
                    _stop_callback()
                except Exception as e:
                    print(f"⚠️ Ошибка в callback экстренной остановки: {e}")

    # Передаем событие дальше (не блокируем)
    return ctypes.windll.user32.CallNextHookEx(_low_level_hook, nCode, wParam, lParam)


def install_emergency_hook(stop_callback=None):
    """
    Установить низкоуровневый хук клавиатуры для ESC
    
    Args:
        stop_callback: функция, вызываемая при нажатии ESC
    
    Returns:
        bool: True если хук установлен успешно
    """
    global _low_level_hook, _stop_callback, _hook_thread, _running

    if _running:
        return True  # Уже установлен

    try:
        _stop_callback = stop_callback
        _running = True

        # Создаем хук - пробуем разные варианты
        hook_proc = HOOKPROC(_low_level_keyboard_handler)
        
        # Пробуем разные варианты получения хендла модуля
        h_module = None
        try:
            # Вариант 1: GetModuleHandleW(None) - текущий процесс
            h_module = ctypes.windll.kernel32.GetModuleHandleW(None)
        except:
            pass
        
        if not h_module:
            try:
                # Вариант 2: GetModuleHandleA для user32
                h_module = ctypes.windll.kernel32.GetModuleHandleA(b'user32.dll')
            except:
                pass
        
        if not h_module:
            # Вариант 3: GetModuleHandleW для kernel32
            try:
                h_module = ctypes.windll.kernel32.GetModuleHandleW('kernel32.dll')
            except:
                h_module = 0  # Последний вариант - NULL для текущего модуля
        
        _low_level_hook = ctypes.windll.user32.SetWindowsHookExA(
            WH_KEYBOARD_LL,
            hook_proc,
            h_module,
            0
        )

        if not _low_level_hook:
            error_code = ctypes.get_last_error()
            raise ctypes.WinError(error_code)

        # Запускаем цикл обработки сообщений в отдельном потоке
        def hook_thread_func():
            MSG = ctypes.Structure
            MSG._fields_ = [
                ('hwnd', wintypes.HWND),
                ('message', wintypes.UINT),
                ('wParam', wintypes.WPARAM),
                ('lParam', wintypes.LPARAM),
                ('time', wintypes.DWORD),
                ('pt', wintypes.POINT)
            ]

            msg = MSG()
            while _running:
                # GetMessage блокирует до получения сообщения
                ret = ctypes.windll.user32.GetMessageW(
                    ctypes.byref(msg),
                    None,
                    0,
                    0
                )
                if ret == 0 or ret == -1:
                    break

                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

        _hook_thread = threading.Thread(target=hook_thread_func, daemon=True)
        _hook_thread.start()

        print("✅ Низкоуровневый хук ESC установлен")
        return True

    except Exception as e:
        print(f"⚠️ Ошибка установки хука ESC: {e}")
        import traceback
        traceback.print_exc()
        _running = False
        return False


def remove_emergency_hook():
    """Удалить низкоуровневый хук"""
    global _low_level_hook, _running

    if not _running:
        return

    try:
        _running = False
        if _low_level_hook:
            result = ctypes.windll.user32.UnhookWindowsHookEx(_low_level_hook)
            if result:
                print("✅ Хук ESC удален")
            _low_level_hook = None
    except Exception as e:
        print(f"⚠️ Ошибка удаления хука: {e}")


def set_stop_flag():
    """
    Установить файл-флаг остановки.
    Использует несколько попыток для надёжности.
    """
    global _stop_flag_check_count
    _stop_flag_check_count += 1
    
    attempts = 3
    for attempt in range(attempts):
        try:
            # Пишем флаг с синхронизацией на диск
            with open(STOP_FLAG_FILE, 'w') as f:
                f.write("STOP")
                f.flush()
                os.fsync(f.fileno())  # Гарантируем запись на диск
            
            print(f"✅ [EMERGENCY_STOP] Флаг остановки установлен (попытка {attempt+1})")
            return True
        except Exception as e:
            if attempt < attempts - 1:
                time.sleep(0.01)  # 10ms между попытками
            else:
                print(f"⚠️ [EMERGENCY_STOP] Не удалось установить флаг: {e}")
                return False
    
    return False


def check_stop_flag():
    """
    Проверить флаг остановки и удалить его.
    Оптимизировано для частых вызовов в цикле бота.
    """
    global _stop_flag_check_count
    _stop_flag_check_count += 1
    
    try:
        # Быстрая проверка существования файла
        if not os.path.exists(STOP_FLAG_FILE):
            return False
        
        # Чтение и проверка содержимого
        with open(STOP_FLAG_FILE, 'r') as f:
            content = f.read().strip()
        
        if content == "STOP":
            # Удаляем флаг
            try:
                os.remove(STOP_FLAG_FILE)
                print(f"✅ [EMERGENCY_STOP] Флаг обнаружен и удален (проверка #{_stop_flag_check_count})")
            except:
                pass
            return True
        
        return False
    except Exception:
        # В случае любой ошибки продолжаем работу
        return False


def clear_all_input():
    """Очистить буфер ввода Windows (на всякий случай)"""
    try:
        # Очищаем очереди сообщений
        ctypes.windll.user32.FlushInput()
    except:
        pass
