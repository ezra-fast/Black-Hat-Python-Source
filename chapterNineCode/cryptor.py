'''
This script uses a hybrid encryption approach to securely encrypt a byte string. The plaintext is encrypted with AES and the AES key is encrypted with a public RSA key.
Decryption involves decrypting the AES key with the private RSA key, parsing the encrypted payload, and decrypting the ciphertext as needed.

Instructions: run a single time with only the generate() function to produce key material as output. Then run the script with the other part of the main function commented in
              and generate() commented out.
'''

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO

import base64
import zlib

def generate():                         # generate private and public RSA keys and write each to their own output file.
    new_key = RSA.generate(2048)
    private_key = new_key.exportKey()
    public_key = new_key.publickey().exportKey()

    with open('key.pri', 'wb') as f:
        f.write(private_key)

    with open('key.pub', 'wb') as f:
        f.write(public_key)

def get_rsa_cipher(keytype):                # take in either 'pub' or 'pri', read the corresponding key file (needs to be in the same directory) and return the cipher object (key) and the size of the RSA key in bytes
    with open(f'key.{keytype}') as f:
        key = f.read()
    rsakey = RSA.importKey(key)
    return (PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes())

def encrypt(plaintext):                                     # encrypt plaintext with AES cipher and return encrypted, encoded payload 
    compressed_text = zlib.compress(plaintext)              # compress the plaintext bytes
    
    session_key = get_random_bytes(16)                      # generate a new session key to be used in the AES cipher
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)        # encrypt the compressed plaintext with the AES cipher

    cipher_rsa, _ = get_rsa_cipher('pub')                                   # obtain the RSA public key
    encrypted_session_key = cipher_rsa.encrypt(session_key)                 # asymmetrically encrypt the session key used in the AES cipher

    msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext       # package up all of the information required to decrypt the ciphertext and the ciphertext itself
    encrypted = base64.encodebytes(msg_payload)                                     # base64 encode the encrypted payload before returning it
    return(encrypted)

def decrypt(encrypted):                                         # decode payload, get RSA cipher, parse encrypted string, decrypt message, decompress message, return plaintext
    encrypted_bytes = BytesIO(base64.decodebytes(encrypted))                    # decode the string into bytes
    cipher_rsa, keysize_in_bytes = get_rsa_cipher('pri')                        # get the RSA private key (key.pri must be in the working directory)

    encrypted_session_key = encrypted_bytes.read(keysize_in_bytes)                  # notice the sequence of the packaging on line 44 to understand this block.
    nonce = encrypted_bytes.read(16)                                                # this block is unpacking and variablizing the different component parts of the encrypted byte string
    tag = encrypted_bytes.read(16)
    ciphertext = encrypted_bytes.read()

    session_key = cipher_rsa.decrypt(encrypted_session_key)             # the session key was encrypted with the public key and is now decrypted with the private key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)          # decrypt (with the now-decrypted AES key) the ciphertext and verify the plaintext's integrity using the digest (tag)

    plaintext = zlib.decompress(decrypted)                              # lastly we decompress the newly decrypted plaintext before returning it
    return plaintext

if __name__ == "__main__":
    # generate()                        # run the script once with only this line, then run with all other lines except this one
    plaintext = b'Test plaintext string'
    print(decrypt(encrypt(plaintext)))