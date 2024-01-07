#!/usr/bin/python2

import urllib2

url = 'https://www.nostarch.com'
response = urllib2.urlopen(url)     # urlopen() returns a file-like object that allows us to read back the body of what the website returns to a GET request
print(response.read())
response.close()