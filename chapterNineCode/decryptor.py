'''
This is a very simple function to decrypt messages sent over exfiltration channels.
'''

from cryptor import decrypt

with open('ciphertext.txt', 'rb') as f:
    contents = f.read()

with open('plaintext.txt', 'wb') as f:
    f.write(decrypt(contents))
