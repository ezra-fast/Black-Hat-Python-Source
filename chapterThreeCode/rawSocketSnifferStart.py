'''
This script sets up a raw socket sniffer, reads a single packet, and the quits
'''

import socket
import os 

HOST = '192.168.0.28'

def main():
    # create raw socket, bind to public interface
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)     # sniffing raw traffic on the interface
    sniffer.bind((HOST, 0))
    #include the IP header in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)     # including the IP headers in the captured packets

    if os.name == 'nt':             # if in windows, send an IOCTL the NIC driver to activate promiscuous mode
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # read one packet
    print(sniffer.recvfrom(65565))      # printing the entire raw packet with no decoding

    # if we're on Windows, turn off promiscuous mode
    if os.name == 'nt':                 # once sniffing is done, turn off promiscuous mode if in windows
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == '__main__':
    main()