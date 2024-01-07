'''
This is a simple multi-threaded TCP server

This can be used to handle callback connections that will transmit exfiltrated data (this is a messy way to handle it)

'''

import socket
import threading

IP = '192.168.0.28'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))                                     # listen at this address on this port
    server.listen(5)                                            # maximum backlog of connections set to 5
    print(f'[*] Listening on {IP}:{PORT}')

    while True:                                                 # wait for connections
        client, address = server.accept()                       # client socket in the client variable, remote connection details in the address variable
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        clientHandler = threading.Thread(target=handleClient, args=(client,))   # each thread begins an instance of handleClient with the client's socket object as the parameter.
        clientHandler.start()

def handleClient(clientSocket):                                 # handling the client connection consists of receiving bytes and sending a simple acknowledgement
    with clientSocket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')

if __name__ == '__main__':
    main()
