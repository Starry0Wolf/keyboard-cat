import random
import pyautogui
import urllib.request
import json
import sys
import os

from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QApplication,
    QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon


# ─── CONFIG FLAGS ───────────────────────────────────────────────────────────
WORD_LIST_PATH = 'many_words.txt'
EMOTICON_LIST_PATH = 'emoticonList.txt'

ENABLE_RANDOM_KEYS      = False
ENABLE_RANDOM_WORDS     = True
ENABLE_RANDOM_EMOTICONS = False
ENABLE_RANDOM_LETTERS   = True
ENABLE_RANDOM_SENTENCES = False  # TODO
ENABLE_MINECRAFT_MODE   = False
ENABLE_SAVE_DOCUMENT    = False

min_interval_sec = 900
max_interval_sec = 7200

# keep alive so Python doesn't GC windows too early
_popup_windows = []

# ─── TRAY ICON ─────────────────────────────────────────────────────────────────
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

# ─── CAT IMAGE FETCHER ──────────────────────────────────────────────────────
def random_cat_pixmap():
    """Fetch a random cat image and return it as an in‑memory QPixmap."""
    try:
        with urllib.request.urlopen("https://api.thecatapi.com/v1/images/search") as r:
            url = json.loads(r.read().decode())[0]["url"]
        with urllib.request.urlopen(url) as r:
            data = r.read()
        pix = QPixmap()
        if pix.loadFromData(data):
            return pix
    except Exception as e:
        print("Error fetching cat image:", e)

    # Return fallback pixmap (e.g., solid black)
    fallback = QPixmap(512, 512)
    fallback.fill(Qt.black)
    return fallback


# ─── POPUP WRAPPER ──────────────────────────────────────────────────────────
def popup_wrapper(func):
    def wrapped(*args, **kwargs):
        popups = []

        # Determine platform-specific window flags
        if sys.platform == "win32":
            flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        elif sys.platform == "darwin":
            flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
        else:
            flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint  # fallback

        for screen in QApplication.screens():
            geo = screen.geometry()
            window = QMainWindow()
            window.setWindowFlags(flags)
            window.setGeometry(geo)
            window.setStyleSheet("background-color: black;")

            # Attributes that prevent focus & allow click-through
            window.setAttribute(Qt.WA_ShowWithoutActivating, True)
            window.setAttribute(Qt.WA_TransparentForMouseEvents, True)

            label = QLabel(window)
            pix = random_cat_pixmap().scaled(
                geo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            label.setPixmap(pix)
            label.setAlignment(Qt.AlignCenter)
            label.setGeometry(window.rect())

            window.setWindowState(window.windowState() | Qt.WindowFullScreen)
            window.show()

            _popup_windows.append(window)
            popups.append(window)

        def run_and_close_all():
            func(*args, **kwargs)
            for w in popups:
                w.close()
                _popup_windows.remove(w)

        QTimer.singleShot(100, run_and_close_all)
    return wrapped

# ─── CHAOS MODES ────────────────────────────────────────────────────────────
@popup_wrapper
def rand_keys():
    """Type random keys, toggling CapsLock occasionally."""
    caps = False
    seq = []
    for _ in range(random.randint(15, 50)):
        if random.randrange(10) == 0:
            seq.append('capslock')
        seq.append(random.choice(pyautogui.KEYBOARD_KEYS))
    for k in seq:
        if k == 'capslock':
            if not caps:
                pyautogui.keyDown('capslock'); caps = True
            else:
                pyautogui.keyUp('capslock'); caps = False
        else:
            pyautogui.press(k)
    pyautogui.keyUp('capslock')

@popup_wrapper
def rand_letters():
    """Type random ASCII characters, toggling CapsLock occasionally."""
    caps = False
    letters = [chr(i) for i in range(32, 127)]
    seq = []
    for _ in range(random.randint(15, 50)):
        if random.randrange(10) == 0:
            seq.append('capslock')
        seq.append(random.choice(letters))
    for ch in seq:
        if ch == 'capslock':
            if not caps:
                pyautogui.keyDown('capslock'); caps = True
            else:
                pyautogui.keyUp('capslock'); caps = False
        else:
            pyautogui.press(ch)
    pyautogui.keyUp('capslock')

@popup_wrapper
def rand_words():
    """Type random words from 'many_words.txt', capitalizing occasionally."""
    try:
        with open(WORD_LIST_PATH) as f:
            words = [w.strip() for w in f if w.strip()]
    except FileNotFoundError:
        print("many_words.txt not found")
        return
    for _ in range(10):
        w = random.choice(words)
        if random.randrange(10) == 0:
            w = w.upper()
        pyautogui.typewrite(w + ' ')

@popup_wrapper
def rand_emoticons():
    """Type random emoticons from 'emoticonList.txt'."""
    try:
        with open(EMOTICON_LIST_PATH) as f:
            emotes = [e.strip() for e in f if e.strip()]
    except FileNotFoundError:
        print("emoticonList.txt not found")
        return
    for _ in range(10):
        pyautogui.typewrite(random.choice(emotes) + ' ')
    pyautogui.press('enter')

@popup_wrapper
def rand_minecraft_mode():
    """Press a random Minecraft movement key."""
    pyautogui.press(random.choice(['w','a','s','d','space','shift']))

def rand_sentences():
    print("rand_sentences is not implemented yet.")
    pass


# ─── SCHEDULER & CORE ───────────────────────────────────────────────────────
def choose_chaos():
    """Pick one enabled mode at random, run it, then press Enter."""
    modes = []
    if ENABLE_RANDOM_KEYS:      modes.append(rand_keys)
    if ENABLE_RANDOM_WORDS:     modes.append(rand_words)
    if ENABLE_RANDOM_EMOTICONS: modes.append(rand_emoticons)
    if ENABLE_RANDOM_LETTERS:   modes.append(rand_letters)
    if ENABLE_RANDOM_SENTENCES: modes.append(rand_sentences)
    if ENABLE_MINECRAFT_MODE:   modes.append(rand_minecraft_mode)

    if not modes:
        print("No chaos modes enabled.")
        return

    if ENABLE_SAVE_DOCUMENT:
        pyautogui.hotkey('ctrl', 's')

    random.choice(modes)()
    pyautogui.keyUp('capslock')
    pyautogui.press('enter')

def schedule_chaos():
    """Run a chaos event, then re-schedule after a random delay."""
    choose_chaos()
    delay = random.randint(min_interval_sec, max_interval_sec) * 1000
    QTimer.singleShot(delay, schedule_chaos)

# ─── MAIN ───────────────────────────────────────────────────────────────────
def main():
    global app
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    tray_icon = QSystemTrayIcon()
    tray_icon.setIcon(QIcon(resource_path("cat.png")))
    tray_icon.setToolTip("Chaos Cat - Running...")
    tray_icon.setVisible(True)

    menu = QMenu()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()

    QTimer.singleShot(0, schedule_chaos)  # Your chaos scheduler
    app.exec_()

if __name__ == "__main__":
    main()
