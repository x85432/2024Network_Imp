# -*- coding: utf-8 -*-
from setting import TOPO1
import sys
""" 
|---My packet format----|
| ARP_pkt = {"type":"ARP", "operation":"", "src ip":"", "dst ip":"", "src mac":"", "dst mac":""}
|
| ICMP_pkt = {"type":"ICMP", "operation":"", "src ip":"", "dst ip":"", "src mac":"", "dst mac":""}
|
| operation : request / reply
"""
def showColor(msg, color):
    if color == "green":
        return "\033[92m"+msg+"\033[0m"
    elif color == "yellow":
        return "\033[93m"+msg+"\033[0m"
    elif color == "red":
        return "\033[91m"+msg+"\033[0m"
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
    
    def sendMsg(self, msg, dst_ip, dst_mac):
        pkt = {"type":"msg", "src ip":self.ip, "src mac":self.mac, "dst ip":dst_ip, "dst mac":dst_mac, "msg":msg}
        if dst_ip == '': #broadcast
            self.send(pkt)
            return
        
        if dst_ip in self.arp_table:
            self.send(pkt)
        else:
            self.ping(dst_ip)
            if dst_ip in self.arp_table:
                self.send(pkt)

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
        if pkt["dst ip"] != self.ip and pkt["dst ip"] != '':  # '' is broadcast
            return #drop
        
        # dst ip == self.ip
        if pkt["type"] == "msg" and (pkt["dst ip"] == self.ip or pkt['dst ip'] == ''): # msg
            print(f"<{self.name}> {showColor('recv', 'green')} msg from {pkt['src ip']}: {pkt['msg']}")

        elif pkt["type"] == "ARP" and pkt["operation"] == "request":  
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
            # broad an ARP request to all host by setting dst = 'ffff'
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

        self.vlan_table = dict() # what vlans this switch has
        self.access_port = dict() # maps port numbers to which VLANs they belong
        self.trunck_port = list()
    
    # TODO: For all first connected port, 
    def add(self, node): # link with other hosts or switches
        self.port_to.append(node) # port to a device
        if node.name in host_dict:
            self.mac_table[node.mac] = len(self.port_to) - 1
            connectedPort = self.mac_table[node.mac]
            self.access_port[connectedPort] = "Native"
        else:
            self.trunck_port.append(len(self.port_to) - 1)

    def show_table(self):
        print(showColor('MAC   | Port', 'yellow'))
        for m in self.mac_table:
            print(f'{m} | {self.mac_table[m]}')

    def show_vlan(self):
        print(showColor('Port | VLAN', 'yellow'))
        for p in self.access_port:
            print("{:<4} | {:<4}".format(p, self.access_port[p]))
        if self.trunck_port != None:
            print(f"Trunck ports: {self.trunck_port}")
        print(showColor('VlanID | status | Configuration Revision', 'yellow'))
        for v in self.vlan_table:
            print("{:<6} | {:<6} | {:<20}".format(v, self.vlan_table[v]["status"], self.vlan_table[v]["Configuration Revision"]))

    def clear(self):
        # clear MAC table entries for this switch
        self.mac_table.clear()
    
    def updateAccessTable(self, vlanID):
        for port in self.access_port:
            if self.access_port[port] == vlanID:
                self.access_port[port] = "Native"

    def updateVLAN(self, vlanID, status, revision):
        updated = False

        if vlanID in self.vlan_table:
            if revision > self.vlan_table[vlanID]["Configuration Revision"]:
                if status == "shutdown":
                    self.vlan_table.pop(vlanID)
                    print(f"<{self.name}> {showColor('Remove', 'green')} VLAN{vlanID}")
                    self.updateAccessTable(vlanID)
                    updated = True
                else:
                    self.vlan_table[vlanID]["status"] = status
                    self.vlan_table[vlanID]["Configuration Revision"] = revision
                    updated = True

        else: # new VLAN
            if status != "shutdown":
                self.vlan_table[vlanID] = {"status":status, "Configuration Revision":revision}
                updated = True
        
        pkt = {"type":"VTP", "newVlanID":vlanID, "status":status,"Configuration Revision":revision}
        if updated: # broadcast to all trunck port
            for port in self.trunck_port:
                node = self.port_to[port]
                node.handle_packet(pkt)

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

    def send(self, outPort, pkt): # send to the specified port
        inPort = self.mac_table[pkt["src mac"]]

        if outPort not in self.trunck_port:
            # pkt in the same switch
            # no tagging
            getVLAN = "Native"
            if inPort in self.trunck_port:
                # we need to untag
                if "VID" in pkt:
                    getVLAN = pkt.pop("VID")
            else:
                getVLAN = self.access_port[inPort]

            if getVLAN == self.access_port[outPort]: # check in the same VLAN
                node = self.port_to[outPort]
                node.handle_packet(pkt)
            else:
                print(f"<{self.name}> {showColor('Drop', 'red')} since {outPort}'s VLAN{self.access_port[outPort]} != {inPort}'s VLAN{getVLAN}")

        else: # send to other switch
            # if the packet is not in the same switch, we need to tag the packet
            # tag the packet with the VLAN of the incoming port
            if inPort in self.trunck_port:
                # already tagged or native
                if "VID" in pkt:
                    print(f"<{self.name}> {showColor('already tagged', 'green')} Port{inPort} pkt with VLAN{pkt['VID']} and send to TrunckPort{outPort}")
                node = self.port_to[outPort]
                node.handle_packet(pkt)
            else:
                getVLAN = self.access_port[inPort]
                if getVLAN != "Native":
                    print(f"<{self.name}> {showColor('tag', 'green')} Port{inPort} pkt with VLAN{getVLAN} and send to TrunckPort{outPort}")
                    pkt["VID"] = getVLAN
                node = self.port_to[outPort]
                node.handle_packet(pkt)
                    
    def flood(self, pkt, inPort):
        # flood to all ports other than inPort
        for idx in range(self.port_n):
            if (idx == inPort): continue
            forwardPKT = pkt.copy()
            self.send(idx, forwardPKT)

    def handle_packet(self, pkt):
        # handle incoming packets
        # print(self.name, "recv pkt", pkt)
        if pkt["type"] == "msg":
            if pkt["dst mac"] in self.mac_table:
                outPort = self.mac_table[pkt["dst mac"]]
                self.send(outPort, pkt)
            elif pkt["dst mac"] == 'ffff': # broadcast
                if pkt["src mac"] not in self.mac_table:
                    self.update_mac(pkt["src mac"])
                self.flood(pkt, self.mac_table[pkt["src mac"]])

        elif pkt["type"] == "VTP":
            self.updateVLAN(pkt["newVlanID"], pkt["status"], pkt["Configuration Revision"])

        elif pkt["type"] == "ARP" and pkt["operation"] == "request":
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

def set_topology(theTOPO):
    global host_dict, switch_dict, server_switch
    hostlist = theTOPO.get_hosts().split(' ')
    switchlist = theTOPO.get_switches().split(' ')
    link_command = theTOPO.get_links()
    ip_dic = theTOPO.get_ip()
    mac_dic = theTOPO.get_mac()
    server_switch_name = theTOPO.get_serverSwitch()
    
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
    
    server_switch = switch_dict[server_switch_name]
def createVLAN(vlanID):
    if vlanID in server_switch.vlan_table:
        print(vlanID, showColor('already exists', 'red'))
        return 1
    
    server_switch.updateVLAN(vlanID, "active", 0)
    return 0

def deleteVLAN(vlanID):
    if vlanID not in server_switch.vlan_table:
        print(vlanID, "does not exist.")
        return 1
    
    # must be new revision
    newRevision = server_switch.vlan_table[vlanID]["Configuration Revision"] + 1
    server_switch.updateVLAN(vlanID, "shutdown", newRevision)
    
    return 0

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
        for s in switch_dict:
            print(f'---------------{s}:')
            switch_dict[s].show_table()
            switch_dict[s].show_vlan()
        print()
    elif tmp in host_dict:
        print(f'ip : mac\n---------------{tmp}')
        host_dict[tmp].show_table()
        
    elif tmp in switch_dict:
        print(f'mac : port\n---------------{tmp}')
        switch_dict[tmp].show_table()
        print(f'port : #VLAN\n---------------{tmp}')
        switch_dict[tmp].show_vlan()
    else:
        return 1
    print()
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
        if len(command_list) == 0:
            continue
        elif len(command_list) == 2 : 
            if command_list[0] == 'show_table':
                wrong = show_table(command_list[1])
            elif command_list[0] == 'clear' :
                wrong = clear(command_list[1])
            elif command_list[0] == "createVLAN":
                vlanNum = int(command_list[1])
                wrong = createVLAN(vlanNum)
            elif command_list[0] == "deleteVLAN":
                vlanNum = int(command_list[1])
                wrong = deleteVLAN(vlanNum)
            else :
                wrong = 1 
        elif len(command_list) == 3:
            if command_list[1] == 'ping':
                wrong = ping(command_list[0], command_list[2])
            elif command_list[1] == 'broadcast':
                if command_list[0] in host_dict:
                    srcHost = host_dict[command_list[0]]
                    srcHost.sendMsg(msg = command_list[2], dst_ip = '', dst_mac = 'ffff')
        
        elif len(command_list) == 4:
            if command_list[0] == "setAccess":
                tarSwitch = command_list[1]
                portNum = int(command_list[2])
                vlanNum = int(command_list[3])
                if tarSwitch in switch_dict:
                    if vlanNum in switch_dict[tarSwitch].vlan_table:
                        switch_dict[tarSwitch].access_port[portNum] = vlanNum
                        print(f"Port{portNum} is set to VLAN{vlanNum} in {tarSwitch}")
                    else:
                        print(f"VLAN{vlanNum} does not exist in {tarSwitch}")
            elif command_list[1] == "send":
                src = command_list[0]
                dst = command_list[2]
                if src in host_dict and dst in host_dict:
                    srcHost = host_dict[src]
                    srcHost.sendMsg(msg = command_list[3], 
                                    dst_ip = host_dict[dst].ip,
                                    dst_mac = host_dict[dst].mac)
            else:
                wrong = 1
        elif len(command_list) > 4 and command_list[1] == "send":
            src = command_list[0]
            dst = command_list[2]
            if src in host_dict and dst in host_dict:
                srcHost = host_dict[src]
                srcHost.sendMsg(msg = ' '.join(command_list[3:]), 
                                dst_ip = host_dict[dst].ip,
                                dst_mac = host_dict[dst].mac)
        else : 
            wrong = 1
        if wrong == 1:
            print('a wrong command')

def main():
    while len(sys.argv) != 2:
        print("Usage: python3 main.py {topology_number}")
        return 1
    if sys.argv[1] == "1":
        set_topology(TOPO1)
    
    run_net()

if __name__ == '__main__':
    main()