'''
This script sniffs a single packet and dumps the contents thereof
'''

from scapy.all import sniff

def packet_callback(packet):    # this is the callback function that is called on the captured packet
    print(packet.show())        # packet.show returns the packet information

def main():
    sniff(prn=packet_callback, count=1)     # sniff on all interfaces until 1 packet is captured; process the packet with the callback function

if __name__ == "__main__":
    main()