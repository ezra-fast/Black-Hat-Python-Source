'''
This is a simple UDP client --> connectionless, this kind of socket connection is good for sending without establishing contact first

'''

import socket

targetHost = '127.0.0.1'
targetPort = 9997

# create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
client.sendto(b'AAABBBCCC', (targetHost, targetPort))

# receive some data --> this is data, addr because UDP returns both the data and the details of the remote host and port
data, addr = client.recvfrom(4096)

print(data.decode())

# closing the connection
client.close()
