'''
This module returns the current environment variables set on the remote machine
'''

import os

def run(**args):
    print("[*] In environment module.")
    return os.environ 

