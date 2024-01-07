'''
This is the server that corresponds to ssh_rcmd.py

Commands typed in at the console of this program are executed on connected clients runnin ssh_rcmd.py
The output is then returned to this server and printed to the console.
'''

import paramiko
import os
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))   # using the SSH key included in the paramiko files

class Server(paramiko.ServerInterface):     # SSH-izing the existing listening socket
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if (username == 'FROZENTERRESTRIAL') and (password == 'FROZEN'):   # fill in credentials here as needed
            return paramiko.AUTH_SUCCESSFUL
        
if __name__ == '__main__':
    server = input('Enter Server Address> ')    # or '192.168.0.41'
    ssh_port = 22
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))           # starting a listening socket
        sock.listen(100)    # increase time as needed
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print(f'[-] Listen failed: {e}')
        sys.exit(1)
    else:
        print('[+] Got a connection!', client, addr)

    bhSession = paramiko.Transport(client)      # this block configures the authentication methods
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)

    chan = bhSession.accept(20)
    if chan is None:
        print('*** No channel.')
        sys.exit(1)
    
    print('[+] Authenticated!')     # console output indicating authentication
    print(chan.recv(1024))          # console output indicating the first message ('ClientConnected') has been received
    chan.send('Welcome to remoteSSH')
    try:
        while True:
            command = input("Enter command $ ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()
