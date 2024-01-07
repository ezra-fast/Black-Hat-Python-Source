'''
This script uses lxml to retrieve the content and parse the links of an HTTP response using the BeautifulSoup module
'''

import requests
from bs4 import BeautifulSoup as bs

url = 'https://bing.com'
r = requests.get(url)
tree = bs(r.text, 'html.parser')        # parse the content into a tree
for link in tree.find_all('a'):         # find all 'a' anchor elements
    print(f'{link.get('href')} -> {link.text}')     # for each anchor element, note the href attribute and the link text

    