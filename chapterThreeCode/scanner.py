'''
This script scans a network subnet by sending out UDP datagrams and parsing the returning ICMP replies.
'''

import ipaddress
import os
import socket
import struct
import sys
import time
import threading

# subnet to target
SUBNET = '10.242.0.0/17'
# string to check ICMP responses for
MESSAGE = 'DINO'    # we include an arbitrary message in outbound datagrams so that ICMP packets we're receiving can be verified to be responses to the scan and not arbitrary pings

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

class ICMP:                 # each instantiation is an ICMP packet; the attributes are the fields.
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]
        
def udp_sender():       # firing datagrams at all hosts in the declared SUBNET
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, 'utf8'), (str(ip), 65212))     # arbitrary port chosen, no service likely to interfere with scanning

class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == 'nt':
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)       # making the socket an attribute of the Scanner class
        self.socket.bind((host, 0))

        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == 'nt':
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    
    def sniff(self):                # sniffing hosts on the subnet
        hosts_up = set([f'{str(self.host)} *'])
        try:
            while True:
                # read a packet
                raw_buffer = self.socket.recvfrom(65535)[0]
                # create an IP header from the first 20 bytes
                ip_header = IP(raw_buffer[0:20])
                # if it's ICMP, we want it
                if ip_header.protocol == 'ICMP':    # investigate all incoming ICMP packets
                    offset = ip_header.ihl * 4      # move past the IP header
                    buf = raw_buffer[offset:offset + 8]     # variablize the ICMP data
                    icmp_header = ICMP(buf)                 # instantiate ICMP object using the data
                    # check for TYPE 3 and CODE
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(SUBNET):    # if it's from the right subnet

                            # make sure it has the magic string
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf8'):       # is it actually a response to our scanner or is it an arbitrary ping
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    print(f"Host Up: {tgt}")        # print the live host as console output
        # handle Keyboard Interrupt
        except KeyboardInterrupt:
            if os.name == 'nt':
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)     # turn on promiscuous mode before leaving if in Windows
            
            print('\nUser interrupted.')
            if hosts_up:
                print(f'\n\nSummary: Hosts up on {SUBNET}')
            for host in sorted(hosts_up):
                print(f'{host}')        # printing all found hosts to the console
            print('')
            sys.exit()
            
# def sniff(host):
#     if os.name == 'nt':
#         socket_protocol = socket.IPPROTO_IP
#     else:
#         socket_protocol = socket.IPPROTO_ICMP

#     sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)     # sniffing raw traffic on the interface
#     sniffer.bind((host, 0))
#     #include the IP header in the capture
#     sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)     # including the IP headers in the captured packets

#     if os.name == 'nt':             # if in windows, send an IOCTL the NIC driver to activate promiscuous mode
#         sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

#     try:
#         while True:             # this loop continuously reads and processes packets, noting the details to the console.
#             # read a packet
#             raw_buffer = sniffer.recvfrom(65535)[0]     # read in the raw packet at layer 3 (Network (IPv4))
#             # create an IP header from the first 20 bytes
#             ip_header = IP(raw_buffer[0:20])
#             # if it's ICMP, we want it
#             if ip_header.protocol == 'ICMP':            # if we've received an ICMP packet
#                 print(f'Protocol: {ip_header.protocol} {ip_header.src_address} -> {ip_header.dst_address}')
#                 print(f'Version: {ip_header.ver}')
#                 print(f'Header Length: {ip_header.ihl} TTL: {ip_header.ttl}')
            
#                 # calculate where our ICMP packet starts
#                 # the ihl field of the IP header tells us how many 32 bit words are contained in the IP header (4 byte blocks)
#                 offset = ip_header.ihl * 4          # where does the ICMP body live in the raw packet? This calculates the length of the IP header and thus, where the layer 3 body begins
#                 buf = raw_buffer[offset:offset + 8]
#                 # create our ICMP structure
#                 icmp_header = ICMP(buf)             # instantiate the ICMP packet
#                 print(f"ICMP: -> Type: {icmp_header.type} Code: {icmp_header.code}")        # print out relevant fields from the packet
            
#             # # print the detected protocol and hosts
#             # print(f'Protocol: {ip_header.protocol} : {ip_header.src_address} -> {ip_header.dst_address}')   # printing packet information
#     except KeyboardInterrupt:
#         # if we're on Windows, turn off promiscuous mode
#         if os.name == 'nt':
#             sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
#         sys.exit()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = input('Enter the current host address> ')        # this should be the address to sniff/listen on
    s = Scanner(host)       # creating the scanner object
    time.sleep(5)
    t = threading.Thread(target=udp_sender)
    t.start()       # starting the upd_sender BEFORE we start sniffing the traffic for live hosts
    s.sniff()
