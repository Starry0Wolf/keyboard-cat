import random
import pyautogui

# 0 is random keys
# 1 is random words
# 2 is random emoticons
# 3 is coherent sentances
# 4 is everything

def chaos_time():
    Randomness = 100
    if random.randint(0,Randomness) == 1:
        choose_chaos()

def choose_chaos():
    TheNumber = random.randint(0,4)
    if TheNumber == 0:
        randKeys()

    elif TheNumber == 1:
        randWords()

    elif TheNumber == 2:
        randEmoticons()

    elif TheNumber == 3:
        randSentence()

    elif TheNumber == 4:
        randLetters()

# all_keys = pyautogui.KEYBOARD_KEYS

TheList = []
CapsMode = False
def Read_txt():
    word_list = []
    try:
        with open('many_words.txt', 'r') as file:
            for line in file:
                # Strip whitespace and skip empty lines
                word = line.strip()
                if word:
                    word_list.append(word)
    except FileNotFoundError:
        print("Error: many_words.txt file not found")
        return []
    return word_list
    
def randKeys():
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

def randLetters():
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

def randWords():
    words = Read_txt()
    if not words:
        return
    
    # Select and type 3 random words
    for _ in range(10):
        word = random.choice(words)
        if random.randint(0,1) == 0:
            # Capitalize the word
            word = word.upper()
        pyautogui.typewrite(word + ' ')


def randEmoticons():

def randSentence():