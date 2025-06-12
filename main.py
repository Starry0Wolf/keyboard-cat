import random
import pyautogui
import time
import threading
import os
import signal

# Configuration flags for different chaos modes
ENABLE_RANDOM_KEYS = False  # Mode 0
ENABLE_RANDOM_WORDS = False  # Mode 1
ENABLE_RANDOM_EMOTICONS = False  # Mode 2
ENABLE_RANDOM_LETTERS = True  # Mode 3
ENABLE_RANDOM_SENTENCES = False  # Mode 4 (not implemented yet)
ENABLE_MINECRAFT_MODE = False # Mode 5

# 0 is random keys
# 1 is random words
# 2 is random emoticons
# 3 is coherent sentances
# 4 is everything

def chaos_time():
    # Remove the fixed randomness and use variable timing instead
    min_seconds = 1  # minimum time between chaos events
    max_seconds = 2  # maximum time between chaos events (27000 = 7.5 hours)

    global running
    while running:
        try:
            sleep_time = random.randint(min_seconds, max_seconds)
            time.sleep(sleep_time)
            if running:  # Check flag before executing
                choose_chaos()
        except Exception as e:
            print(f"Error during chaos: {e}")
            time.sleep(5)  # Wait a bit before retrying

def start_chaos_daemon():
    global chaos_thread, running
    running = True
    # Write PID to file
    with open('chaos.pid', 'w') as f:
        f.write(str(os.getpid()))
    chaos_thread = threading.Thread(target=chaos_time, daemon=True)
    chaos_thread.start()
    return chaos_thread

def choose_chaos():
    # Create a list of enabled modes
    enabled_modes = []
    if ENABLE_RANDOM_KEYS:
        enabled_modes.append(0)
    if ENABLE_RANDOM_WORDS:
        enabled_modes.append(1)
    if ENABLE_RANDOM_EMOTICONS:
        enabled_modes.append(2)
    if ENABLE_RANDOM_LETTERS:
        enabled_modes.append(3)
    if ENABLE_RANDOM_SENTENCES:
        enabled_modes.append(4)
    if ENABLE_MINECRAFT_MODE:
        enabled_modes.append(5)
    
    if not enabled_modes:
        print("No chaos modes are enabled!")
        return
    
    # Choose from enabled modes only
    if ENABLE_MINECRAFT_MODE == True:
        randMC()
    else:
        TheNumber = random.choice(enabled_modes)
        
        if TheNumber == 0:
            randKeys()
        elif TheNumber == 1:
            randWords()
        elif TheNumber == 2:
            randEmoticons()
        elif TheNumber == 3:
            randLetters()
        elif TheNumber == 4:
            pass  # TODO: implement randSentence()

        pyautogui.press('enter')

# all_keys = pyautogui.KEYBOARD_KEYS

TheList = []
CapsMode = False
def Read_txt(file):
    word_list = []
    try:
        with open(file, 'r') as file:
            for line in file:
                # Strip whitespace and skip empty lines
                # word = line.strip()
                # if word:
                word = line.strip()
                if word:  # Only append non-empty lines
                    word_list.append(word)
    except FileNotFoundError:
        print("Error: many_words.txt file not found")
        return []
    return word_list
    
def randMC():
    # W, A, S, D, space
    Chances = random.randint(0, 5)
    if Chances == 0:
        pyautogui.press('W')
    elif Chances == 1:
        pyautogui.press('A')
    elif Chances == 2:
        pyautogui.press('S')
    elif Chances == 3:
        pyautogui.press('D')
    elif Chances == 4:
        pyautogui.press('space')
    elif Chances == 5:
        pyautogui.press('shift')
    
def randKeys():
    global CapsMode  # Properly scope the global variable
    TheList = []  # Move list creation inside function
    for i in range(10):
        all_keys = pyautogui.KEYBOARD_KEYS
        if random.randint(0,1) == 0:
            TheList.append('capslock')
        TheList.append(random.choice(all_keys))
    print(TheList)
    for item in TheList:
        if item == 'capslock':
            if CapsMode == False:
                pyautogui.keyDown('capslock')
                CapsMode = True
            else:
                pyautogui.keyUp('capslock')
                CapsMode = False
        else:
            pyautogui.press(item)
    TheList.clear()
    pyautogui.keyUp('capslock')
    CapsMode = False
    print('Keys mode activated')

def randLetters():
    global CapsMode  # Properly scope the global variable
    TheList = []  # Move list creation inside function
    for i in range(10):
        all_letters = [chr(i) for i in range(ord('a'), ord('z')+1)]
        if random.randint(0,1) == 0:
            TheList.append('capslock')
        TheList.append(random.choice(all_letters))
    print(TheList)
    for item in TheList:
        if item == 'capslock':
            if CapsMode == False:
                pyautogui.keyDown('capslock')
                CapsMode = True
            else:
                pyautogui.keyUp('capslock')
                CapsMode = False
        else:
            pyautogui.press(item)
    TheList.clear()
    pyautogui.keyUp('capslock')
    CapsMode = False
    print('Letters mode activated')

def randWords():
    words = Read_txt('many_words.txt')
    if not words:
        return
    
    # Select and type 3 random words
    for _ in range(10):
        word = random.choice(words)
        if random.randint(0,1) == 0:
            # Capitalize the word
            word = word.upper()
        pyautogui.typewrite(word + ' ')
    print('Words mode activated')


def randEmoticons():
    emotes = Read_txt('emoticonList.txt')
    if not emotes:
        return
    
    # Select and type 3 random words
    for _ in range(10):
        word = random.choice(emotes)
        pyautogui.typewrite(word + ' ')

    print('Emoticon mode activated')
    pyautogui.press('enter')

# def randSentence():
    # TODO: use ollama maybe for some stupid sentences?
    # TODO: implement this
    

# Add signal handler
def signal_handler(signum, frame):
    global running
    running = False
    print("\nChaos cat is going to sleep...")
    os._exit(0)

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    print("Chaos cat is now running in the background...")
    print("Press Ctrl+C to exit")
    
    # Start the chaos thread
    chaos_thread = start_chaos_daemon()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nChaos cat is going to sleep...")