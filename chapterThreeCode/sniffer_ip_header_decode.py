

import ipaddress
import os
import socket
import struct
import sys

class IP:                           # each instance represents an IPv4 header from a received packet
    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)       # the first format character '<' specifies the endianness of the data
        self.ver = header[0] >> 4           # no way to extract a nibble, so bitwise operations must be performed for the first two fields
        self.ihl = header[0] & 0xF

        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.sum = header[7]
        self.src = header[8]
        self.dst = header[9]

        # human readable IP addresses
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        # map protocol constants to their names
        self.protocol_map = {1 : "ICMP", 6 : "TCP", 17 : "UDP"}
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print(f'{e} No protocol for {self.protocol_num}')
            self.protocol = str(self.protocol_num)

def sniff(host):
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)     # sniffing raw traffic on the interface
    sniffer.bind((host, 0))
    #include the IP header in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)     # including the IP headers in the captured packets

    if os.name == 'nt':             # if in windows, send an IOCTL the NIC driver to activate promiscuous mode
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:             # this loop continuously reads and processes packets, noting the details to the console.
            # read a packet
            raw_buffer = sniffer.recvfrom(65535)[0]     # read in the raw packet at layer 3 (Network (IPv4))
            # create an IP header from the first 20 bytes
            ip_header = IP(raw_buffer[0:20])            # create an IPv4 header object out of the first 20 bytes of the captured packet
            # print the detected protocol and hosts
            print(f'Protocol: {ip_header.protocol} : {ip_header.src_address} -> {ip_header.dst_address}')   # printing packet information
    except KeyboardInterrupt:
        # if we're on Windows, turn off promiscuous mode
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = input('Enter the current host address> ')        # this should be the address to sniff/listen on
    sniff(host)