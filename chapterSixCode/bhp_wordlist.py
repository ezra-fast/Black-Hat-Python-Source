'''
This script can be added as an extension to Burp Suite to produce a custom wordlist based on the text content of all pages of a web application.

Instructions:
    - add the script as an extension
    - Dashboard > New Live Task
    - Choose Predefined Task > Add all links observed in traffic through Proxy to site map (populating the Site Map)
    - Browse to target website
    - Select all requests in the Target tab
    - Extensions > BHP Wordlist > Create Wordlist
    - Extensions > Output
'''

from burp import IBurpExtender
from burp import IContextMenuFactory

from java.util import ArrayList
from javax.swing import JMenuItem

from datetime import datetime
from HTMLParser import HTMLParser

import re

class TagStripper(HTMLParser):      # stripping the HTML tags out of the HTTP response being processed
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_text = []

    def handle_data(self, data):        # storing the page text in an attribute (list)
        self.page_text.append(data)

    def handle_comment(self, data):     # this method supports adding comments in the code to the wordlist as well
        self.page_text.append(data)

    def strip(self, html):
        self.feed(html)                 # feeding the HTML code to the base class (HTMLParser)
        return " ".join(self.page_text)     # returning the page text as a string


class BurpExtender(IBurpExtender, IContextMenuFactory):     # Creating a context menu in the Burp Suite GUI
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self.context    = None
        self.hosts      = set()

        # start with something we know is common
        self.wordlist   = set(['password'])         # initializing the password set with 'password'; set is used because we don't want duplicates

        # set up our extension
        callbacks.setExtensionName("BHP Wordlist")
        callbacks.registerContextMenuFactory(self)

        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Create Wordlist", actionPerformed=self.wordlist_menu))

        return menu_list

    def wordlist_menu(self, event):                     # this method handles menu clicks
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()

        for traffic in http_traffic:
            http_service    = traffic.getHttpService()
            host            = http_service.getHost()        # getting and saving the name of the responding host
            self.hosts.add(host)
            http_response = traffic.getResponse()           # retrieving the HTTP response and feeding it to the get_words() method
            if http_response:
                self.get_words(http_response)

        self.display_wordlist()
        return

    def get_words(self, http_response):
        headers, body = http_response.tostring().split('\r\n\r\n', 1)       # separating the HTTP response into parts for processing

        # skip non-text responses
        if headers.lower().find("context-type: text") == -1:                # making sure we're only processing text-based responses
            return

        tag_stripper = TagStripper()
        page_text = tag_stripper.strip(body)            # the TagStripper class strips the HTML code from the rest of the page text

        words = re.findall("[a-zA-Z]\w{2,}", page_text)     # find all the words that start with an alphabetical character and 2 or more word characters

        for word in words:
            # filter out long strings
            if len(word) <= 20:
                self.wordlist.add(word.lower())         # adding the identified strings under the character limit to the wordlist in lowercase

        return

    def mangle(self, word):                     # taking in a single word and permuting it several different ways to produce guesses
        year        = datetime.now().year
        suffixes    = ["", "1", "!", year]
        mangled     = []

        for password in (word, word.capitalize()):
            for suffix in suffixes:
                mangled.append("%s%s" % (password, suffix))
        
        return mangled

    def display_wordlist(self):                 # reminder to console which site was used to make this wordlist
        print("#!comment: BHP Wordlist for site(s) %s" % ", ".join(self.hosts))

        for word in sorted(self.wordlist):      # mangle each word in the wordlist and print the results
            for password in self.mangle(word):
                print(password)

