'''
This script demonstrates making a GET request in Python3.x
'''

import urllib.parse
import urllib.request

url = 'http://boodelyboo.com'
with urllib.request.urlopen(url) as response:           # urlopen() is what actually makes the request to the target URL
    content = response.read()

print(content)