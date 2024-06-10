# -*- coding: utf-8 -*-
from setting import get_hosts, get_switches, get_links, get_ip, get_mac
""" 
|---My packet format----|

| ARP_pkt = {"type":"ARP", "operation":"", "src ip":"", "dst ip":"", "src mac":"", "dst mac":""}
|
| ICMP_pkt = {"type":"ICMP", "operation":"", "src ip":"", "dst ip":"", "src mac":"", "dst mac":""}
|
| operation : request / reply
"""

class host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac 
        self.port_to = None
        self.arp_table = dict() # maps IP addresses to MAC addresses
    def add(self, node):
        self.port_to = node
    def show_table(self):
        for i in self.arp_table:
            print(f'{i} : {self.arp_table[i]}')
    def clear(self):
        # clear ARP table entries for this host
        self.arp_table.clear()
        
    def update_arp(self, newHostIp, newHostMac):
        # update ARP table with a new entry
        # for host in host_dict: # Search in all hosts
        #     if host_dict[host].ip == newHostIp:

        """Don't use global information"""
        # self.arp_table[newHostIp] = host_dict[host].mac
        self.arp_table[newHostIp] = newHostMac
        return
            
    def send(self, pkt): # host will not help propagate others's pkt
        # print(self.name, "send pkt", pkt)
        node = self.port_to # get node connected to this host
        node.handle_packet(pkt) # send packet to the connected node

    def handle_packet(self, pkt):
        # determine the destination MAC here
        '''
            Hint :
                if the packet is the type of arp request, destination MAC would be 'ffff'.
                else, check up the arp table.
        '''
        # print(self.name, "recv pkt", pkt)
        # handle incoming packets
        if pkt["dst ip"] != self.ip:
            return #drop
        
        # dst ip == self.ip
        if pkt["type"] == "ARP" and pkt["operation"] == "request":  
            if pkt["src ip"] not in self.arp_table:
                self.update_arp(pkt["src ip"], pkt["src mac"])
            reply_pkt = {
                            "type":"ARP",
                            "operation":"reply", 
                            "src mac":self.mac, # the meaning of reply is replying own mac addr
                            "src ip":self.ip, 
                            "dst mac":pkt["src mac"],
                            "dst ip":pkt["src ip"]
                         }
            self.send(reply_pkt)

        elif pkt["type"] == "ARP" and pkt["operation"] == "reply":
            if pkt["src ip"] not in self.arp_table:
                self.update_arp(pkt["src ip"], pkt["src mac"])
            # ICMP request
            request_pkt = {
                            "type":"ICMP",
                            "operation":"request", 
                            "src ip":self.ip,
                            "dst ip":pkt["src ip"],
                            "src mac":self.mac,
                            "dst mac":pkt["src mac"]
                         }
            self.send(request_pkt)

        elif pkt["type"] == "ICMP" and pkt["operation"] == "request":
            reply_pkt = {
                            "type":"ICMP",
                            "operation":"reply", 
                            "src ip":self.ip,
                            "dst ip":pkt["src ip"],
                            "src mac":self.mac,
                            "dst mac":pkt["src mac"]
                         }
            self.send(reply_pkt)
        elif pkt["type"] == "ICMP" and pkt["operation"] == "reply":
            pass
            # print("ICMP success after", self.name, "pinging.")

    def ping(self, dst_ip):  
        # handle a ping request
        if dst_ip in self.arp_table:
            request_pkt = {
                            "type"  :"ICMP",
                            "operation" : "request",
                            "src ip":self.ip,
                            "dst ip":dst_ip,
                            "src mac":self.mac,
                            "dst mac":self.arp_table[dst_ip]
                          }
            self.send(request_pkt)
        else:
            # broadcast an ARP request to all host by setting dst = 'ffff'
            request_pkt = {
                            "type"   :"ARP",
                            "operation" : "request",
                            "src mac":self.mac, 
                            "src ip" :self.ip, 
                            "dst mac" :'ffff',
                            "dst ip"  : dst_ip
                          }
            self.send(request_pkt)
            # After recv ARP reply, 
            # 1. update arp table
            # 2. send ICMP-request to h2

class switch:
    def __init__(self, name, port_n):
        self.name = name
        self.mac_table = dict() # maps MAC addresses to port numbers
        self.port_n = port_n # number of ports on this switch
        self.port_to = list() 
    def add(self, node): # link with other hosts or switches
        self.port_to.append(node)
    def show_table(self):
        for m in self.mac_table:
            print(f'{m} : {self.mac_table[m]}')
    def clear(self):
        # clear MAC table entries for this switch
        self.mac_table.clear()
    def update_mac(self, mac):
        # update MAC table with a new entry
        """How to NOT use GLOBAL information"""
        """We can use incoming port? """

        """NO, We need to take the empty port for a switch. Since"""
        """outPort for a switch is not the inPort of another switch"""
        
        """NO concept which called "empty port", we need to use device
           to give the ports.
        """
        idx = 0
        for dev in self.port_to:
            if (dev.name in host_dict) and (dev.mac == mac):
                idx = self.port_to.index(dev)
                break
            elif (dev.name in switch_dict) and (mac in dev.mac_table):
                idx = self.port_to.index(dev)
                # if we have another one mac in this dev's mac_table, we assign the same port
                break
        
        self.mac_table[mac] = idx        

    def send(self, idx, pkt): # send to the specified port
        # idx: target port
        # node may be host or switch
        # print(self.name, "port", idx, "send pkt", pkt)
        
        node = self.port_to[idx]
        node.handle_packet(pkt) # pass pkt to "port_to" node
        

    def flood(self, pkt, inPort):
        # flood to all ports other than inPort
        for idx in range(self.port_n):
            if (idx == inPort): continue
            self.send(idx, pkt)

    def handle_packet(self, pkt):
        # handle incoming packets
        # print(self.name, "recv pkt", pkt)

        if pkt["type"] == "ARP" and pkt["operation"] == "request":
            # Learning incoming port for mac table
            if pkt["src mac"] not in self.mac_table: 
                self.update_mac(pkt["src mac"])
            
            if pkt["dst mac"] == 'ffff': # flood
                self.flood(pkt, self.mac_table[pkt["src mac"]])
            elif pkt["dst mac"] in self.mac_table: # searching
                # searching mac table will get the port of learned port
                self.send(self.mac_table[pkt["dst mac"]], pkt)
            else: 
                # searching failed, just flood
                self.flood(pkt, self.mac_table[pkt["src mac"]])

        else: # hold for ARP request, ICMP request, ICMP reply
            # Learning incoming port for mac table
            if pkt["src mac"] not in self.mac_table: 
                self.update_mac(pkt["src mac"])
            

            if pkt["dst mac"] in self.mac_table: # searching
                # searching mac table will get the port of learned port

                self.send(self.mac_table[pkt["dst mac"]], pkt)
            else: 
                # searching failed, just flood
                self.flood(pkt, inPort = self.mac_table["src mac"])

def add_link(tmp1, tmp2): # create a link between two nodes
    if tmp1 in host_dict:
        node1 = host_dict[tmp1]
    else:
        node1 =  switch_dict[tmp1]
    if tmp2 in host_dict:
        node2 = host_dict[tmp2]
    else:
        node2 = switch_dict[tmp2]
    node1.add(node2)

def set_topology():
    global host_dict, switch_dict
    hostlist = get_hosts().split(' ')
    switchlist = get_switches().split(' ')
    link_command = get_links()
    ip_dic = get_ip()
    mac_dic = get_mac()
    
    host_dict = dict() # maps host names to host objects
    switch_dict = dict() # maps switch names to switch objects
    
    for h in hostlist:
        host_dict[h] = host(h, ip_dic[h], mac_dic[h])
    for s in switchlist:
        switch_dict[s] = switch(s, len(link_command.split(s))-1)
    for l in link_command.split(' '):
        [n0, n1] = l.split(',')
        add_link(n0, n1)
        add_link(n1, n0)

    for s in switchlist:
        switch_dict[s].port_n = len(switch_dict[s].port_to)
    

def ping(tmp1, tmp2): # initiate a ping between two hosts
    global host_dict, switch_dict
    if tmp1 in host_dict and tmp2 in host_dict : 
        node1 = host_dict[tmp1]
        node2 = host_dict[tmp2]
        node1.ping(node2.ip)
    else : 
        return 1 # wrong 
    return 0 # success 


def show_table(tmp): # display the ARP or MAC table of a node
    if tmp == 'all_hosts':
        print(f'ip : mac')
        for h in host_dict:
            print(f'---------------{h}:')
            host_dict[h].show_table()
        print()
    elif tmp == 'all_switches':
        print(f'mac : port')
        for s in switch_dict:
            print(f'---------------{s}:')
            switch_dict[s].show_table()
        print()
    elif tmp in host_dict:
        print(f'ip : mac\n---------------{tmp}')
        host_dict[tmp].show_table()
    elif tmp in switch_dict:
        print(f'mac : port\n---------------{tmp}')
        switch_dict[tmp].show_table()
    else:
        return 1
    return 0


def clear(tmp):
    wrong = 0
    if tmp in host_dict:
        host_dict[tmp].clear()
    elif tmp in switch_dict:
        switch_dict[tmp].clear()
    else:
        wrong = 1
    return wrong


def run_net():
    while(1):
        wrong = 0 
        command_line = input(">> ")
        command_list = command_line.strip().split(' ')
        
        if command_line.strip() =='exit':
            return 0
        if len(command_list) == 2 : 
            if command_list[0] == 'show_table':
                wrong = show_table(command_list[1])
            elif command_list[0] == 'clear' :
                wrong = clear(command_list[1])
            else :
                wrong = 1 
        elif len(command_list) == 3 and command_list[1] == 'ping' :
            wrong = ping(command_list[0], command_list[2])
        else : 
            wrong = 1
        if wrong == 1:
            print('a wrong command')

    
def main():
    set_topology()
    run_net()


if __name__ == '__main__':
    main()