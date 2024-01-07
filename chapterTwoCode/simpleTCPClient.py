'''
This is a simple TCP Client --> This can be used to connect to a machine and then send and receive data until the connection is terminated

This connects, sends data bytes, receive data back, prints the received data, and then closes connection

'''

import socket

targetHost = 'www.google.com'
targetPort = 80

# Creating the socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the client to targetHost
client.connect((targetHost, targetPort))

# Send some data
client.send(b'GET / HTTP/1.1\r\nHost: google.com\r\n\r\n')

# Receivce some data
response = client.recv(4096)

print(response.decode())

# Closing the connection
client.close()
