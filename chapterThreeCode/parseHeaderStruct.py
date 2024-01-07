'''
This script uses the struct and ipaddress modules to create an IP class, which has as attributes all fields in the IPv4 header
'''

import ipaddress
import struct

'''
Instantiating the class:
    mypacket = IP(buff)
    print(f'{mypacket.src_address} -> {mypacket.dst_address}')
'''

'''
struct format characters are as follows:
    - B : 1 byte unsigned char
    - H : 2 byte unsigned short
    - s : byte array that requires a byte length specification; 4s means 4-byte string

The format string '<BBHHHBBH4s4s' follows the structure of the standard IPv4 header
'''

class IP:
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