'''
module that lists files and directories in the current working directory
'''

import os

def run(**args):                        
    print("[*] In dirlister module.")
    files = os.listdir(".")
    return str(files)

