'''
This script demonstrates making a simple POST request in Python3
'''

import urllib.parse
import urllib.request

info = {'user' : 'tim', 'passwd' : 'password'}      # defining the data we need to send in the body of the request
data = urllib.parse.urlencode(info).encode()        # turning that data into bytes

req = urllib.request.Request(url, data)             # making the request object
with urllib.request.urlopen(req) as response:       # making the request itself with the urlopen() function
    content = response.read()

print(content)                                      # printing the response