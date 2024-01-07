#!/usr/bin/python3
# Description: This code comes from BlackHatPython 2nd Edition; it is a relatively simple implementation of a TCP proxy
'''
[*] Four main function:
            - display communictions between the local host and remote machines to the console (hexdump())
            - receive data from an incoming socket from either the local machine/a remote machine (receive_from())
            - manage the traffic direction between the local and remote machines (proxy_handler())
            - set up a listening socket and pass it to our proxy_handler() (server_loop())

'''

'''
Example Command:
        - sudo python3.11 TCProxy.py 127.0.0.1 21 10.243.8.88 21 True
        - sudo python3.10 TCProxy.py <local IP> <local port> <destination address> <destination port> True
        	- pass traffic through the proxy by setting it up to listen and initiating the process to access the service at the proxy address (ex: remote ftp server would be accessed at the localIP:21)
'''

import sys
import socket
import threading

# HEX_FILTER contains all printable ascii characters, and non-printable characters are replaced with '.'

HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])       # first condition selects for ascii, else '.'

# hexdump():
#       - take input as bytes or string and print the corresponding hexdump to the console
#       - AKA printing the hex and ascii characters of each packet

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):              # making sure that the input is a string
        src = src.decode()                  # decoding the input string

    results = list()        # will contain the hex value of the index of the first byte in the word, hex value of the word, and printable ascii of the word
    for i in range(0, len(src), length):        # length is 16 bytes 
        word = str(src[i:i+length])             # making the 'word' (16 bytes?!)
        
        printable = word.translate(HEX_FILTER)  # translating the hex values for printable character values using the global HEX_FILTER
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x}  {hexa:<{hexwidth}}  {printable}')     # formatting the output similar to hexdump -C
    if show:
        for line in results:
            print(line)                         # if show == True, show the results of this process as output
    else:
        return results                          # else return the output as return value

# receive_from() is used for both ends of the proxy to receive the data
#       - the socket object is passed as parameter

def receive_from(connection):
    buffer = b''                                       # create an empty bytes buffer
    connection.settimeout(30)                # timeout set to 5 seconds; increase as necessary
    try:
        while True:                                          # fill buffer with data until no more data, or timeout
            data = connection.recv(4096)        # accumulate responses from the socket
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer                                       # return the now full buffer to the caller (local or remote machine)

# The following functions can be filled in to modify request/response packets before they are sent:
#       - fuzzing, authentication tests, modify headers, etc.

def request_handler(buffer):
    # packet modifications
    return buffer

def response_handler(buffer):
    # packet modifications
    return buffer

# proxy_handler:
#       - This is the main functionality of the socket
#               - connect to the remote host
#               - check to make sure we don't need to initiate connection and request data first before going into the loop
#               - enter loop
#                       - use receive_from() for both sides of the communication
#                               - accepts a socket connected object and performs a receive
#                       - dump the contents of the packet
#                       - give the output to response_handler()
#                       - send the received buffer to the local client

#       - The loop reads from local client, processes, sends to remote host; reads from remote host, processes, and passes to local client; over and over again until there is no data left.
#       - Once there is no data left, both the local and remote sockets are closed and the loop terminates

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print(f"[<==] Sending {len(remote_buffer)} bytes to localhost")
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = f"[==>] Received {len(local_buffer)} bytes from localhost"
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Send to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote")
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections")
            break

# server_loop:

'''
    - create socket
    - binds to the local host and listens
    - in the loop:
            - if fresh connection comes in, hand it to proxy_handler() in a new thread
            - proxy_handler() handles the sending and receiving between the parties in the data stream
'''

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f'problem on bind: {e}')

        print(f"[!!] Failed to listen on {local_host}:{local_port}")
        print(f"[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = f"> Received incoming connection from {addr[0], addr[1]}"
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

# main function
#       - variablize command line arguments and spin up the server loop to listen
#         for connections

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end=' ')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == "__main__":
    main()
