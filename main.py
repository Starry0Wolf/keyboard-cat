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
    "min_interval_sec": 10,
    "max_interval_sec": 50,
    "enable_auto_update": True,
    "show_tooltip_countdown": False,
}

_popup_windows = []
_next_chaos_in_ms = 0
_running_chaos = False
_chaos_timer = None


# ─── TRAY SETUP ─────────────────────────────────────────────────────
def create_tray(app):
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon("cat.png"))
    tray.setToolTip("Keyboard Cat Chaos")

    menu = QMenu()

    snooze_action = QAction("Snooze 5 minutes")
    snooze_action.triggered.connect(lambda: snooze_chaos(300))
    menu.addAction(snooze_action)

    settings_action = QAction("Settings")
    settings_action.triggered.connect(show_settings)
    menu.addAction(settings_action)

    quit_action = QAction("Exit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.show()
    return tray

# ─── CAT IMAGE FETCHER ─────────────────────────────────────────────
def random_cat_pixmap():
    try:
        with urllib.request.urlopen("https://api.thecatapi.com/v1/images/search") as r:
            url = json.loads(r.read().decode())[0]["url"]
        with urllib.request.urlopen(url) as r:
            data = r.read()
        pix = QPixmap()
        if pix.loadFromData(data):
            return pix
    except Exception:
        pass
    fallback = QPixmap(512, 512)
    fallback.fill(Qt.black)
    return fallback


# ─── POPUP DECORATOR ───────────────────────────────────────────────
def popup_wrapper(func):
    def wrapped(*args, **kwargs):
        global _running_chaos
        if _running_chaos:
            return
        _running_chaos = True
        popups = []

        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        if sys.platform == "win32":
            flags |= Qt.Tool
        elif sys.platform == "darwin":
            flags |= Qt.WindowDoesNotAcceptFocus

        for screen in QApplication.instance().screens():
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
            global _running_chaos
            _running_chaos = False

        QTimer.singleShot(3000, run_and_close_all)  # show cat for 3s

    return wrapped


# ─── CHAOS FUNCTIONS ───────────────────────────────────────────────
@popup_wrapper
def test_chaos():
    print("Chaos triggered!")


def schedule_chaos():
    global _next_chaos_in_ms, _chaos_timer
    delay = random.randint(config["min_interval_sec"], config["max_interval_sec"]) * 1000
    _next_chaos_in_ms = delay

    if config["show_tooltip_countdown"]:
        tray.setToolTip(f"Next chaos in {delay // 1000} sec")

    _chaos_timer = QTimer()
    _chaos_timer.setSingleShot(True)
    _chaos_timer.timeout.connect(run_chaos)
    _chaos_timer.start(delay)


def run_chaos():
    test_chaos()
    schedule_chaos()


def snooze_chaos(seconds):
    if _chaos_timer:
        _chaos_timer.stop()
    QTimer.singleShot(seconds * 1000, schedule_chaos)


# ─── SETTINGS UI ───────────────────────────────────────────────────
def show_settings():
    win = QWidget()
    win.setWindowTitle("Settings")

    layout = QVBoxLayout()

    # Timing
    time_row = QHBoxLayout()
    min_box = QSpinBox(); min_box.setValue(config["min_interval_sec"])
    max_box = QSpinBox(); max_box.setValue(config["max_interval_sec"])
    time_row.addWidget(QLabelWidget("Min delay")); time_row.addWidget(min_box)
    time_row.addWidget(QLabelWidget("Max delay")); time_row.addWidget(max_box)
    layout.addLayout(time_row)

    # Options
    tooltip_toggle = QCheckBox("Show tooltip countdown")
    tooltip_toggle.setChecked(config["show_tooltip_countdown"])
    layout.addWidget(tooltip_toggle)

    update_toggle = QCheckBox("Enable auto-update")
    update_toggle.setChecked(config["enable_auto_update"])
    layout.addWidget(update_toggle)

    save_btn = QPushButton("Save")
    def save():
        config["min_interval_sec"] = min_box.value()
        config["max_interval_sec"] = max_box.value()
        config["show_tooltip_countdown"] = tooltip_toggle.isChecked()
        config["enable_auto_update"] = update_toggle.isChecked()
        win.close()
    save_btn.clicked.connect(save)
    layout.addWidget(save_btn)

    win.setLayout(layout)
    win.show()


# ─── MAIN ─────────────────────────────────────────────────────────
def main():
    global tray
    app = QApplication([])
    tray = create_tray(app)
    schedule_chaos()
    app.exec_()

if __name__ == "__main__":
    main()