import tkinter
import keyboard
import time
import pywinctl
import json
import threading
import os
from tkinter import ttk

fullStr = ""
waiting = False
active = False
queuedString = ""
startTime = time.time()
coaTime = 10
queueTermination = False

toggleHotkey = "Alt+Ctrl+Z"
abilityKeybind = "F"

class Lotfi(tkinter.Entry):
    def _is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def __init__(self, master=None, **kwargs):
        self.var = tkinter.StringVar()
        tkinter.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace_add('write', self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        if self._is_float(self.get()): 
            # the current value is only digits; allow this
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this 
            self.set(self.old_value)

def saveSettings():
    global toggleHotkey
    global abilityKeybind
    data = {
        "toggleHotkey": toggleHotkey,
        "abilityKeybind": abilityKeybind,
        "coaTime": coaTime
    }
    jsonData = json.dumps(data)
    if os.path.exists("settings.json"):
        with open("settings.json", 'w') as f:
            f.write(jsonData)
            f.close()
    else:
        f = open("settings.json", 'x')
        f.write(jsonData)
        f.close()

def loadSettings():
    global toggleHotkey
    global abilityKeybind
    global coaTime
    if not os.path.exists("settings.json"):
        print('No settings found, using defaults.')
        return
    with open("settings.json", 'r') as f:
        data = json.loads(f.read())
        toggleHotkey = data["toggleHotkey"]
        abilityKeybind = data["abilityKeybind"]
        coaTime = data["coaTime"]
        toggleButton["text"] = data["toggleHotkey"]
        keybindButton["text"] = data["abilityKeybind"]
        keyboard.remove_hotkey(toggleActive)
        keyboard.add_hotkey(data["toggleHotkey"].lower(), toggleActive, suppress=True)
        f.close()

def kbCallbackForToggle(key:keyboard.KeyboardEvent):
    global waiting
    global fullStr
    global queuedString
    global toggleHotkey
    if key.event_type == 'down' and waiting and pywinctl.getActiveWindowTitle() == "CtA Chainer":
        if key.name == "esc":
            waiting = False
            keyboard.unhook(kbCallbackForToggle)
        elif ("shift" in key.name) and "Shift" not in queuedString:
            queuedString += key.name.title() + "+"
        elif ("ctrl" in key.name) and "Ctrl" not in queuedString:
            queuedString += key.name.title() + "+"
        elif ("alt" in key.name) and "Alt" not in queuedString:
            queuedString += key.name.title() + "+"
        elif "shift" not in key.name and "alt" not in key.name and "ctrl" not in key.name and key.name != "esc":
            queuedString += key.name.upper()
            keyboard.unhook(kbCallbackForToggle)
            fullStr = queuedString
            toggleHotkey = queuedString
            waiting = False
def kbCallbackForAbility(key:keyboard.KeyboardEvent):
    global waiting
    global fullStr
    global queuedString
    global abilityKeybind
    if key.event_type == 'down' and waiting and pywinctl.getActiveWindowTitle() == "CtA Chainer":
        if key.name == "esc":
            waiting = False
            keyboard.unhook(kbCallbackForAbility)
        elif len(key.name) == 1:
            queuedString += key.name.upper()
            keyboard.unhook(kbCallbackForAbility)
            fullStr = queuedString
            abilityKeybind = queuedString
            waiting = False

def setToggle():
    def thred():
        global waiting
        global fullStr
        global queuedString
        fullStr = toggleButton["text"]
        toggleButton["state"] = "disabled"
        keybindButton["state"] = "disabled"
        toggleButton["text"] = "Press any key..."
        waiting = True
        queuedString = ""
        keyboard.hook(kbCallbackForToggle)
        while waiting and not queueTermination:
            if not queueTermination:
                time.sleep(0.001)
        if queueTermination:
            return
        toggleButton["state"] = "normal"
        keybindButton["state"] = "normal"
        toggleButton["text"] = fullStr
        keyboard.clear_hotkey(toggleActive)
        keyboard.add_hotkey(fullStr.lower(), toggleActive, suppress=True)
    threading.Thread(target=thred).start()

def setBind():
    def thred():
        global waiting
        global fullStr
        global queuedString
        fullStr = keybindButton["text"]
        toggleButton["state"] = "disabled"
        keybindButton["state"] = "disabled"
        keybindButton["text"] = "Press any key..."
        waiting = True
        queuedString = ""
        keyboard.hook(kbCallbackForAbility)
        while waiting and not queueTermination:
            if not queueTermination:
                time.sleep(0.001)
        if queueTermination:
            return
        toggleButton["state"] = "normal"
        keybindButton["state"] = "normal"
        keybindButton["text"] = fullStr
    threading.Thread(target=thred).start()
    
window = tkinter.Tk()
window.title("CtA Chainer")
window.iconbitmap('icon-small.ico')
window.geometry("300x164")

activeFrame = ttk.Frame(master=window)
activeLabel = ttk.Label(master=activeFrame, text="Active:")
activeBool = ttk.Label(master=activeFrame, text=str(active), foreground="#CF0000", font="Segoe-UI 9 bold")
activeLabel.pack(side='left')
activeBool.pack(side='right')
activeFrame.pack(pady=6)

togFrame = ttk.Frame(master=window)
toggleLabel = ttk.Label(master=togFrame, text="Toggle Keybind:")
toggleButton = ttk.Button(master=togFrame, text="Alt+Ctrl+Z", command=setToggle)
toggleLabel.pack(side='left')
toggleButton.pack(side='right')
togFrame.pack(pady=10)

keyFrame = ttk.Frame(master=window)
keybindLabel = ttk.Label(master=keyFrame, text="Ability Keybind:")
keybindButton = ttk.Button(master=keyFrame, text="F", command=setBind)
keybindLabel.pack(side='left')
keybindButton.pack(side='right')
keyFrame.pack(pady=10)

inputFrame = ttk.Frame(master=window)
inputLavel = ttk.Label(master=inputFrame, text="Time Between Usages:")
inputField = Lotfi(master=inputFrame)
inputField.insert(0, "10")
inputLavel.pack(side='left')
inputField.pack(side='right', padx=2)
inputFrame.pack(pady=10)

def toggleActive():
    global active
    global activeLabel
    active = not active
    activeBool["text"] = str(active)
    activeBool["foreground"] = "#00CF00" if active else "#CF0000"

keyboard.add_hotkey(toggleButton["text"].lower(), toggleActive, suppress=True)

def main():
    global startTime
    global coaTime
    global active
    global keybindButton
    global inputField
    while not queueTermination:
        coaTime = float(inputField.var.get())
        if (time.time()-startTime) > coaTime:
            print('queued for cta')
            if active and 'Roblox' in pywinctl.getActiveWindowTitle():
                keyboard.press_and_release(keybindButton["text"].lower())
                startTime = time.time()
                print('did cta, new start is ' + str(startTime))
        time.sleep(0.25)

if __name__ == "__main__":
    mainThread = threading.Thread(target=main)
    mainThread.start()
    loadSettings()
    print('Running!')
    window.mainloop()
    keyboard.unhook_all()
    keyboard.remove_all_hotkeys()
    queueTermination = True
    saveSettings()