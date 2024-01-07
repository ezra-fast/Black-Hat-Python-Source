'''
This script uses the ctypes module to define an IP class, which has as attributes all the fields in an IPv4 header.
    - IP inherits from ctypes.Structre, which uses __new__ to initialize the _fields_ structure, which is mandatory
    - this initialization of the _fields_ structure is done before the object is created with __init__
'''

from struct import *
import socket
import struct

class IP(Structure):        # the IP class inherits from the ctypes Structure class
    _fields_ = [        # the _fields_ structure defines each part of the IP header
        ("version",         c_ubyte,    4),         # 4 bit unsigned char
        ("ihl",             c_ubyte,    4),         # 4 bit unsigned char
        ("tos",             c_ubyte,    8),         # 1 byte char
        ("len",             c_ushort,   16),        # 2 byte unsigned short
        ("id",              c_ushort,   16),        # 2 byte unsigned short
        ("offset",          c_ushort,   16),        # 2 byte unsigned short
        ("ttl",             c_ubyte,    8),         # 1 byte char
        ("protocol_num",    c_ubyte,    8),         # 1 byte char
        ("sum",             c_ushort,   16),        # 2 byte unsigned short
        ("src",             c_uint32,   32),        # 4 byte unsigned int
        ("dst",             c_uint32,   32)         # 3 byte unsigned int
    ]
    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        # human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
