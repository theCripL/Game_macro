import time
from datetime import datetime
import threading
import ctypes
import traceback
import sys
import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
SETTINGS_BAT = os.path.join(BASE_DIR, "settings.bat")

DEFAULT_KEYS = ["left", "right", "e"]
DEFAULT_TOGGLE = "F10"

user32 = ctypes.windll.user32

def ensure_config():
    """Если config.json отсутствует — открываем мастер настройки"""
    if not os.path.exists(CONFIG_PATH):
        if os.path.exists(SETTINGS_BAT):
            p = subprocess.Popen(["cmd.exe", "/c", SETTINGS_BAT], creationflags=subprocess.CREATE_NEW_CONSOLE)
            p.wait()
        else:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "first_setup_done": True,
                    "components_verified": True,
                    "toggle_key": DEFAULT_TOGGLE,
                    "keys": DEFAULT_KEYS
                }, f, indent=2)

ensure_config()

import pystray
from PIL import Image, ImageDraw
import interception

# Инициализируем перехват устройств ядра
interception.auto_capture_devices(keyboard=True, mouse=True)

is_active = False
is_running = True
lock = threading.Lock()
worker_thread = None
tray_icon = None

def log(message):
    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{now}] {message}")

def get_virtual_key_code(key_name):
    name = str(key_name).upper().strip()
    vk_map = {
        "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
        "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
        "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
        "NUMPAD0": 0x60, "NUMPAD1": 0x61, "NUMPAD2": 0x62,
        "NUMPAD3": 0x63, "NUMPAD4": 0x64, "NUMPAD5": 0x65,
        "NUMPAD6": 0x66, "NUMPAD7": 0x67, "NUMPAD8": 0x68,
        "NUMPAD9": 0x69, "TAB": 0x09, "CAPS": 0x14, "CAPSLOCK": 0x14,
        "TILDE": 0xC0, "`": 0xC0, "SPACE": 0x20
    }
    if name in vk_map:
        return vk_map[name]
    if len(name) == 1:
        vk = user32.VkKeyScanW(ord(name[0]))
        if vk != -1:
            return vk & 0xFF
    return 0x79

def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                keys = data.get("keys", DEFAULT_KEYS)
                toggle = data.get("toggle_key", DEFAULT_TOGGLE)
                clean_keys = [str(k).lower().strip() for k in keys if k][:5]
                return clean_keys, str(toggle).upper().strip()
    except Exception as e:
        log(f"Ошибка чтения конфига: {e}")
    return DEFAULT_KEYS, DEFAULT_TOGGLE

def press_down(key_name):
    if key_name in ("left", "right", "middle"):
        interception.mouse_down(key_name)
    else:
        interception.key_down(key_name)

def press_up(key_name):
    if key_name in ("left", "right", "middle"):
        interception.mouse_up(key_name)
    else:
        interception.key_up(key_name)

def hold_worker():
    keys, _ = load_config()
    log(f">>> [СТАРТ] Удержание клавиш: {keys}")
    
    try:
        for k in keys:
            press_down(k)
            time.sleep(0.05)

        log(">>> [УДЕРЖАНИЕ АКТИВНО]")

        while is_active and is_running:
            for k in keys:
                press_down(k)
            time.sleep(0.03)

    except Exception as e:
        log(f"ОШИБКА в потоке удержания: {e}")
        traceback.print_exc()
    finally:
        log("<<< [СБРОС] Отпускание клавиш...")
        for k in reversed(keys):
            try:
                press_up(k)
                time.sleep(0.02)
            except Exception:
                pass
        log("<<< [УСПЕХ] Все клавиши отпущены")

def toggle():
    global is_active, worker_thread
    with lock:
        is_active = not is_active
        if is_active:
            log("ТУМБЛЕР -> [РЕЖИМ ВКЛ]")
            worker_thread = threading.Thread(target=hold_worker, daemon=True)
            worker_thread.start()
        else:
            log("ТУМБЛЕР -> [РЕЖИМ ВЫКЛ]")

def key_listener():
    last_pressed = False
    while is_running:
        _, toggle_name = load_config()
        vk_code = get_virtual_key_code(toggle_name)

        state = user32.GetAsyncKeyState(vk_code)
        pressed = bool(state & 0x8000)

        if pressed and not last_pressed:
            toggle()

        last_pressed = pressed
        time.sleep(0.02)

def create_tray_image():
    image = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, 60, 60), fill="#1E88E5", outline="#1565C0", width=2)
    return image

def open_settings(icon, item):
    if os.path.exists(SETTINGS_BAT):
        try:
            os.startfile(SETTINGS_BAT)
        except Exception as e:
            log(f"Ошибка открытия настроек: {e}")
    else:
        log(f"Файл {SETTINGS_BAT} не найден!")

def exit_app(icon, item):
    global is_running, is_active
    is_active = False
    is_running = False
    time.sleep(0.1)
    icon.stop()
    sys.exit(0)

def main():
    global tray_icon

    listener_thread = threading.Thread(target=key_listener, daemon=True)
    listener_thread.start()

    icon_image = create_tray_image()
    menu = pystray.Menu(
        pystray.MenuItem("AION 2 Macro", None, enabled=False),
        pystray.MenuItem("Настройки", open_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Выход", exit_app)
    )
    
    tray_icon = pystray.Icon("AION2_Macro", icon_image, "AION 2 Macro", menu)
    tray_icon.run()

if __name__ == "__main__":
    main()