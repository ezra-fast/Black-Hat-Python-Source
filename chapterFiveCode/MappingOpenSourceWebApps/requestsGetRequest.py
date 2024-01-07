'''
This script demonstrates how to make an HTTP GET request using the requests module
'''

import requests

url = 'http://boodelyboo.com'
response = requests.get(url)        # GET request

data = {'user' : 'ezra', 'passwd' : 'password'}
response = requests.post(url, data=data)        # POST request
print(response.text)        # response.text = string; respponse.content = bytestring