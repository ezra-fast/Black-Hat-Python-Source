'''
This script boils down a wordlist into a queue and then sets THREADS number of threads against the target to brute force file and directory names

Because this program is multi-threaded, writing the output to a singular output file still needs to be implemented
'''

import queue
import requests
import threading
import sys

AGENT = "Mozilla /5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
TARGET = 'http://192.168.0.46/'
THREADS = 10
WORDLIST = "/home/ezra/blackHatPython/chapterFiveCode/BruteForcingDirectoriesAndFiles/all.txt"

def get_words(resume=None):

    def extend_words(word):
        if "." in word:
            words.put(f"/{word}")           # if file name (because of extension) leave the end
        else:
            words.put(f"/{word}/")          # if dir name (no extension) append a '/'

        for extension in EXTENSIONS:
            words.put(f'/{word}{extension}')
        
    with open(WORDLIST) as f:
        raw_words = f.read()                # read in all words from the wordlist

    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():          # go through each line in the wordlist
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f'Resuming wordlist from: {resume}')
        else:
            print(word)
            extend_words(word)
    return words                        # return the queue of words to be used against the target

def dir_bruter(words,):                  # parameter is the queue object that was previously prepared (filled with words)
    headers = {'User-Agent' : AGENT}    # using the predefined agent so that the packets are inconspicuous
    while not words.empty():            # go through the entire queue of words to try
        url = f"{TARGET}{words.get()}"
        try:
            r = requests.get(url, headers=headers)      # sending the request
        except requests.exceptions.ConnectionError:
            sys.stderr.write('x');sys.stderr.flush()
            continue
        if r.status_code == 200:
            print(f"Success ({r.status_code}: {url})")        # if we can reach it, print to console and add to queue
        elif r.status_code == 404:
            sys.stderr.write('.');sys.stderr.flush()
        else:
            print(f"{r.status_code} => {url}")

if __name__ == "__main__":
    sys.stderr = open('/dev/null', 'w')         # redirecting stderr to /dev/null so that it won't be printed to the console
    words = get_words()
    print('Press return to continue.')
    sys.stdin.readline()
    for _ in range(THREADS):                    # spinning up THREADS amount of threads to do the actual brute forcing
        t = threading.Thread(target=dir_bruter, args=(words,))
        t.start()
