'''
This script walks down the target web application, inserting each full filepath into a queue called webpaths
    - this script required a local copy of the WordPress source at the hardcoded directory

This script was successfully tested against the OWASP DVWA to produce myanswers.txt
'''

import contextlib
from email import contentmanager
import os
import queue
import requests
import sys
import threading
import time

FILTERED = ['.jpg', '.gif', '.png', '.css']         # we are not interested in files with these extensions
TARGET = 'http://192.168.0.46/login.php'            # (the remote target website)
THREADS = 10

answers = queue.Queue()             # this queue object will store the file paths that we have found locally
web_paths = queue.Queue()           # this queue object will store the files that we'll attempt to locate on the remote server

def gather_paths():                 # gather the local path of all target files we wish to locate on the remote machine 
    for root, _, files in os.walk('.'):
        for fname in files:
            if os.path.splitext(fname)[1] in FILTERED:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
            print(path)
            web_paths.put(path)     # add the full path of all files whose extension is not in FILTERED

@contextlib.contextmanager
def chdir(path):                    # chdir() is a context manager
    '''
    On enter, change directory to specified path
    On exit, change directory back to the original
    '''
    this_dir = os.getcwd()          # initializing the function by saving the current directory so that it can be returned to later
    os.chdir(path)                  # now changing into the new path
    try:
        yield                       # yield execution control back to gather_paths()
    finally:
        os.chdir(this_dir)          # once control is returned back from gather_paths(), return to the original saved directory

def test_remote():                  # this is the workhorse of this script
    while not web_paths.empty():        # go through all files in the queue
        path = web_paths.get()
        url = f'{TARGET}{path}'         # add the path to the target base URL
        time.sleep(2)               # the target may have throttling/lockout
        r = requests.get(url)           # sending the request
        if r.status_code == 200:        # if accessible
            answers.put(url)            # put the accessible url on the successful queue
            sys.stdout.write('+')
        else:
            sys.stdout.write('x')
        sys.stdout.flush()

def run():
    mythreads = list()
    for i in range(THREADS):                # spawn the number of threads defined globally
        print(f'Spawning thread {i}')
        t = threading.Thread(target=test_remote)        # set each thread to run an instance of test_remote() (processing a single file from the Queue of files)
        mythreads.append(t)
        t.start()

    for thread in mythreads:
        thread.join()                       # gracefully wait for all threads to finish running

if __name__ == "__main__":
    with chdir("/home/ezra/Downloads/wordpress"):       # context managers help to ensure that the program is executing in the correct dir and doesn't get unexpedtedly lost
        gather_paths()
    input('Press return to continue.')                  # review results before testing the remote instance

    run()                                               # test the remote instance
    with open('myanswers.txt', 'w') as f:
        while not answers.empty():
            f.write(f'{answers.get()}\n')               # write the links with response code 200 to the output file 'myanswers.txt'
        print('done')

