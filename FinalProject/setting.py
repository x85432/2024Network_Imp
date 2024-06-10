class TOPO1:
    def get_hosts():
        command = 'h1 h2 h3 h4 h5'
        return command 
    
    def get_switches():
        command = 's1 s2 s3'
        return command 
    
    def get_ip():
        ip_dict = dict()
        ip_dict["h1"] = 'h1ip'
        ip_dict["h2"] = 'h2ip'
        ip_dict["h3"] = 'h3ip'
        ip_dict["h4"] = 'h4ip'
        ip_dict["h5"] = 'h5ip'
        return ip_dict
    
    def get_mac():
        mac_dict = dict()
        mac_dict["h1"] = 'h1mac'
        mac_dict["h2"] = 'h2mac'
        mac_dict["h3"] = 'h3mac'
        mac_dict["h4"] = 'h4mac'
        mac_dict["h5"] = 'h5mac'
        return mac_dict
        
    def get_links():
        command = "h1,s1 h2,s1 h3,s2 h4,s2" #level 1
        command += " s1,s3 s2,s3" #level 2
        command += " s3,h5" #level 3
        return command
        
    def get_serverSwitch():
        return "s3"

# class TOPO2:
    