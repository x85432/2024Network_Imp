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
        for host in host_dict: #host is name
            if host_dict[host].mac == mac:
                idx = self.port_to.index(host_dict[host]) # find the "node" in port list
                self.mac_table[mac] = idx
                return

    def send(self, idx, pkt): # send to the specified port
        node = self.port_to[idx] 
        node.handle_packet(pkt) # pass to "port_to" node

    def flood(self, pkt, inPort):
        for idx in len(self.port_to):
            if idx == inPort:
                continue
            self.send(idx, pkt)
            
    def handle_packet(self, pkt):
        # handle incoming packets       
        if pkt["type"] == "ARP" and pkt["operation"] == "request":
            if pkt["src mac"] not in self.mac_table:
                self.update_mac(pkt["src mac"])
            
            if pkt["dst mac"] == 'ffff':
                self.flood(pkt, inPort = self.mac_table["src mac"])
            elif pkt["dst mac"] in self.mac_table:
                self.send(self.mac_table[pkt["dst mac"]], pkt)
            else:
                self.flood(pkt, inPort = self.mac_table["src mac"])