#!/usr/bin/python2

import urllib2

url = 'https://www.nostarch.com'
headers = {'User-Agent': "Googlebot"}       # defining a custom header; the format is a dictionary where the fields are the keys

request = urllib2.Request(url, headers=headers)     # Request takes the given parameters and creates the web request object
response = urllib2.urlopen(request)                 # urrlib2.urlopen() is what actually makes the call

print(response.read())
response.close()