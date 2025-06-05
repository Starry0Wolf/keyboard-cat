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

def randEmoticons():

def randSentence():