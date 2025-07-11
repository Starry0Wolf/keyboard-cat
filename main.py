import random
import pyautogui
import urllib.request
import json
import sys
import os
import tempfile
import shutil
import subprocess

from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QApplication,
    QSystemTrayIcon, QMenu, QAction,
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel as QLabelWidget, QSpinBox,
    QCheckBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon

# ─── CONFIG & GLOBALS ──────────────────────────────────────────────
APP_VERSION = "1.0.0"
GITHUB_REPO = "starry0wolf/keyboard-cat"
WORD_LIST_PATH = 'many_words.txt'
EMOTICON_LIST_PATH = 'emoticonList.txt'

config = {
    "enable_random_keys": False,
    "enable_random_words": True,
    "enable_random_emoticons": False,
    "enable_random_letters": True,
    "enable_random_sentences": False,
    "enable_minecraft_mode": False,
    "enable_save_document": False,
    "min_interval_sec": 50,
    "max_interval_sec": 120,
    "enable_auto_update": False,  # ON by default
    "show_tooltip_countdown": False,
}

_popup_windows = []
_next_chaos_in_ms = 0


# ─── RESOURCE PATH ───────────────────────────────────────────────
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)


# ─── CAT IMAGE FETCHER ───────────────────────────────────────────
def random_cat_pixmap():
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

    fallback = QPixmap(512, 512)
    fallback.fill(Qt.black)
    return fallback


# ─── POPUP WRAPPER ──────────────────────────────────────────────
def popup_wrapper(func):
    def wrapped(*args, **kwargs):
        popups = []

        if sys.platform == "win32":
            flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        elif sys.platform == "darwin":
            flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
        else:
            flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

        for screen in QApplication.screens():
            geo = screen.geometry()
            window = QMainWindow()
            window.setWindowFlags(flags)
            window.setGeometry(geo)
            window.setStyleSheet("background-color: black;")
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


# ─── CHAOS MODES ──────────────────────────────────────────────────
@popup_wrapper
def rand_keys():
    caps = False
    seq = []
    for _ in range(random.randint(15, 50)):
        if random.randrange(10) == 0:
            seq.append('capslock')
        seq.append(random.choice(pyautogui.KEYBOARD_KEYS))
    for k in seq:
        if k == 'capslock':
            if not caps:
                pyautogui.keyDown('capslock')
                caps = True
            else:
                pyautogui.keyUp('capslock')
                caps = False
        else:
            pyautogui.press(k)
    pyautogui.keyUp('capslock')

@popup_wrapper
def rand_letters():
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
                pyautogui.keyDown('capslock')
                caps = True
            else:
                pyautogui.keyUp('capslock')
                caps = False
        else:
            pyautogui.press(ch)
    pyautogui.keyUp('capslock')

@popup_wrapper
def rand_words():
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
    pyautogui.press(random.choice(['w','a','s','d','space','shift']))

def rand_sentences():
    print("rand_sentences is not implemented yet.")


# ─── SCHEDULER & CORE ─────────────────────────────────────────────
def choose_chaos():
    modes = []
    if config["enable_random_keys"]:      modes.append(rand_keys)
    if config["enable_random_words"]:     modes.append(rand_words)
    if config["enable_random_emoticons"]: modes.append(rand_emoticons)
    if config["enable_random_letters"]:   modes.append(rand_letters)
    if config["enable_random_sentences"]: modes.append(rand_sentences)
    if config["enable_minecraft_mode"]:   modes.append(rand_minecraft_mode)

    if not modes:
        print("No chaos modes enabled.")
        return

    if config["enable_save_document"]:
        pyautogui.hotkey('ctrl', 's')

    random.choice(modes)()
    pyautogui.keyUp('capslock')
    pyautogui.press('enter')


def schedule_chaos():
    global _next_chaos_in_ms
    choose_chaos()
    delay = random.randint(config["min_interval_sec"], config["max_interval_sec"]) * 1000
    _next_chaos_in_ms = delay
    QTimer.singleShot(delay, schedule_chaos)


# ─── SETTINGS DIALOG ──────────────────────────────────────────────
class SettingsDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chaos Cat Settings")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        # Timing inputs
        timing_layout = QHBoxLayout()
        timing_layout.addWidget(QLabelWidget("Min Interval (sec):"))
        self.min_spin = QSpinBox()
        self.min_spin.setRange(1, 3600)
        self.min_spin.setValue(config["min_interval_sec"])
        timing_layout.addWidget(self.min_spin)

        timing_layout.addWidget(QLabelWidget("Max Interval (sec):"))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 3600)
        self.max_spin.setValue(config["max_interval_sec"])
        timing_layout.addWidget(self.max_spin)
        layout.addLayout(timing_layout)

        # Chaos modes checkboxes
        self.chk_keys = QCheckBox("Random Keys")
        self.chk_keys.setChecked(config["enable_random_keys"])
        layout.addWidget(self.chk_keys)

        self.chk_words = QCheckBox("Random Words")
        self.chk_words.setChecked(config["enable_random_words"])
        layout.addWidget(self.chk_words)

        self.chk_emotes = QCheckBox("Random Emoticons")
        self.chk_emotes.setChecked(config["enable_random_emoticons"])
        layout.addWidget(self.chk_emotes)

        self.chk_letters = QCheckBox("Random Letters")
        self.chk_letters.setChecked(config["enable_random_letters"])
        layout.addWidget(self.chk_letters)

        self.chk_sentences = QCheckBox("Random Sentences")
        self.chk_sentences.setChecked(config["enable_random_sentences"])
        layout.addWidget(self.chk_sentences)

        self.chk_minecraft = QCheckBox("Minecraft Mode")
        self.chk_minecraft.setChecked(config["enable_minecraft_mode"])
        layout.addWidget(self.chk_minecraft)

        self.chk_save_doc = QCheckBox("Save Document Before Chaos")
        self.chk_save_doc.setChecked(config["enable_save_document"])
        layout.addWidget(self.chk_save_doc)

        self.chk_tooltip = QCheckBox("Show Time Until Next Event on Hover")
        self.chk_tooltip.setChecked(config["show_tooltip_countdown"])
        layout.addWidget(self.chk_tooltip)

        self.chk_auto_update = QCheckBox("Enable Auto Update")
        self.chk_auto_update.setChecked(config["enable_auto_update"])
        layout.addWidget(self.chk_auto_update)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save(self):
        # Save settings back to config dict
        min_val = self.min_spin.value()
        max_val = self.max_spin.value()
        if min_val > max_val:
            QMessageBox.warning(self, "Invalid Timing", "Min interval cannot be greater than max interval.")
            return

        config["min_interval_sec"] = min_val
        config["max_interval_sec"] = max_val
        config["enable_random_keys"] = self.chk_keys.isChecked()
        config["enable_random_words"] = self.chk_words.isChecked()
        config["enable_random_emoticons"] = self.chk_emotes.isChecked()
        config["enable_random_letters"] = self.chk_letters.isChecked()
        config["enable_random_sentences"] = self.chk_sentences.isChecked()
        config["enable_minecraft_mode"] = self.chk_minecraft.isChecked()
        config["enable_save_document"] = self.chk_save_doc.isChecked()
        config["show_tooltip_countdown"] = self.chk_tooltip.isChecked()
        config["enable_auto_update"] = self.chk_auto_update.isChecked()

        self.close()


# ─── AUTO UPDATE ────────────────────────────────────────────────

def get_running_exe_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    return None

def download_file(url, dest_path):
    try:
        with urllib.request.urlopen(url) as r, open(dest_path, 'wb') as f:
            shutil.copyfileobj(r, f)
        return True
    except Exception as e:
        print(f"Failed to download update: {e}")
        return False

def install_update(new_exe_path):
    current_exe = get_running_exe_path()
    if not current_exe:
        print("Not a frozen executable; cannot auto-update.")
        return

    update_script = f"""
    @echo off
    timeout /t 2 /nobreak >nul
    copy /y "{new_exe_path}" "{current_exe}"
    start "" "{current_exe}"
    """

    script_path = os.path.join(tempfile.gettempdir(), "update.bat")
    with open(script_path, 'w') as f:
        f.write(update_script)

    subprocess.Popen(["cmd", "/c", script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
    app.quit()

def check_for_updates():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read().decode())
            latest_version = data['tag_name']
            if latest_version > APP_VERSION:
                assets = data.get('assets', [])
                for asset in assets:
                    if asset['name'].endswith('.exe'):
                        return latest_version, asset['browser_download_url']
    except Exception as e:
        print("Update check failed:", e)
    return None, None

def auto_update_check():
    if config.get("enable_auto_update", False):
        latest_version, download_url = check_for_updates()
        if latest_version:
            print(f"Auto-updating to {latest_version} ...")
            tmp_path = os.path.join(tempfile.gettempdir(), "KeyboardCatNew.exe")
            success = download_file(download_url, tmp_path)
            if success:
                install_update(tmp_path)


# ─── TRAY ICON & MAIN ─────────────────────────────────────────────
class TrayApp(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon(resource_path("cat.png")))
        self.setToolTip("Chaos Cat - Running...")
        self.settings_dialog = None

        # Build menu
        menu = QMenu()

        self.action_snooze = QAction("Snooze 5 Minutes")
        self.action_snooze.triggered.connect(self.snooze)
        menu.addAction(self.action_snooze)

        self.action_settings = QAction("Settings")
        self.action_settings.triggered.connect(self.open_settings)
        menu.addAction(self.action_settings)

        self.action_exit = QAction("Exit")
        self.action_exit.triggered.connect(QApplication.instance().quit)
        menu.addAction(self.action_exit)

        self.setContextMenu(menu)

        # Timer for chaos events
        self.chaos_timer = QTimer()
        self.chaos_timer.timeout.connect(schedule_chaos)
        self.chaos_timer.start(1000)  # Will be reset immediately

        # Timer for countdown tooltip update
        self.tooltip_timer = QTimer()
        self.tooltip_timer.timeout.connect(self.update_tooltip)
        self.tooltip_timer.start(1000)

    def snooze(self):
        self.chaos_timer.stop()
        QTimer.singleShot(5 * 60 * 1000, self.resume)

    def resume(self):
        schedule_chaos()
        self.chaos_timer.start()

    def open_settings(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog()
            self.settings_dialog.show()
            self.settings_dialog.destroyed.connect(self.settings_closed)
        else:
            self.settings_dialog.activateWindow()

    def settings_closed(self):
        # Update timers and tooltip based on new config
        self.chaos_timer.stop()
        schedule_chaos()
        self.chaos_timer.start()

    def update_tooltip(self):
        if config["show_tooltip_countdown"]:
            seconds_left = _next_chaos_in_ms // 1000
            self.setToolTip(f"Chaos Cat - Next event in {seconds_left} sec")
        else:
            self.setToolTip("Chaos Cat - Running...")

def main():
    global app
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    tray = TrayApp()
    tray.show()

    # Start chaos scheduling immediately
    schedule_chaos()

    # Auto-update timer: check every 30 minutes
    update_timer = QTimer()
    update_timer.timeout.connect(auto_update_check)
    update_timer.start(30 * 60 * 1000)
    auto_update_check()  # also check once immediately

    app.exec_()

if __name__ == "__main__":
    main()
