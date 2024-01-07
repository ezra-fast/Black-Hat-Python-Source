'''
This script uses lxml to retrieve the content and parse the links of an HTTP response using the lxml module
'''

from io import BytesIO              # io is needed so we can use a bytestring as a file object when we parse the HTTP response
from lxml import etree

import requests

url = 'https://nostarch.com'
r = requests.get(url)           # sending the GET request
content = r.content             # content is of type 'bytes'

parser = etree.HTMLParser()                                         # instantiating the parser itself
content = etree.parse(BytesIO(content), parser=parser)              # parsing using the parser; expects a file-like object or a filename; the BytesIO() function allows the bytestring content from the response as the file-like object
for link in content.findall('//a'):                                 # find all the 'a' anchor elements
    print(f"{link.get('href')} -> {link.text}")                     # anchor tags define links, href attribute specifies the URL of the link
