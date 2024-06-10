class host:
""" 
host.clear() 
"""
    def clear(self):
        # clear ARP table entries for this host
        self.arp_table.clear()

"""
Update ARP Table
"""
    def update_arp(self, newHostIp, newHostMac):
        # update ARP table with a new entry
        for host in host_dict: # Search in all hosts
            if host_dict[host].ip == newHostIp:
                """Don't use global information"""
                # self.arp_table[newHostIp] = host_dict[host].mac
                self.arp_table[newHostIp] = newHostMac
                return
"""
Host.send(pkt)
"""
    def send(self, pkt): # host will not help propagate others's pkt
        # print(self.name, "send pkt", pkt)
        node = self.port_to # get node connected to this host
        node.handle_packet(pkt) # send packet to the connected node
"""
Host handle received pkt
"""
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
"""
host.ping(dst_ip)
"""
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
"""
Switch clear up mac table
"""
    def clear(self):
        # clear MAC table entries for this switch
        self.mac_table.clear()
"""
Switch update mac table
"""
    def update_mac(self, mac):
        # update MAC table with a new entry
        """How to NOT use GLOBAL information"""
        """We can use incoming port? """

        """NO, We need to take the empty port for a switch. Since"""
        """outPort for a switch is not the inPort of another switch"""

        allPort = {i for i in range(self.port_n)}
        usedPort = {self.mac_table[m] for m in self.mac_table}

        etyPort = list(allPort - usedPort)
        etyPort.sort() # take the smallest port

        if etyPort:
            self.mac_table[mac] = etyPort[0]
        else:
            print("Ports are all connected")

        # we need to update port_to list also, such that port_to[port] can
        # correspond to the device
        def swap(port_to, id1, id2):
            tmp = port_to[id1]
            port_to[id1] = port_to[id2]
            port_to[id2] = tmp
        
        idx = 0
        for dev in self.port_to:
            if (dev.name in host_dict) and (dev.mac == mac):
                idx = self.port_to.index(dev)
                break
            elif (dev.name in switch_dict) and (mac in dev.mac_table):
                idx = self.port_to.index(dev)
                break
        
        swap(self.port_to, idx, self.mac_table[mac])

        
"""
Switch send pkt
"""
    def send(self, idx, pkt): # send to the specified port
        # idx: target port
        # node may be host or switch
        # print(self.name, "port", idx, "send pkt", pkt)
        
        node = self.port_to[idx]
        node.handle_packet(pkt) # pass pkt to "port_to" node
        
"""
Switch flood to all ports other than incoming port
"""
    def flood(self, pkt, inPort):
        # flood to all ports other than inPort
        for idx in range(self.port_n):
            if (idx == inPort): continue
            self.send(idx, pkt)
"""
Switch handle received pkt
"""
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
