def get_hosts():
    command = 'h1 h2 h3 h4 h5 h6 h7 h8'
    return command 
def get_switches():
    command = 's1 s2 s3 s4 s5 s6 s7'
    return command 
def get_ip():
    ip_dict = dict()
    ip_dict["h1"] = 'h1ip'
    ip_dict["h2"] = 'h2ip'
    ip_dict["h3"] = 'h3ip'
    ip_dict["h4"] = 'h4ip'
    ip_dict["h5"] = 'h5ip'
    ip_dict["h6"] = 'h6ip'
    ip_dict["h7"] = 'h7ip'
    ip_dict["h8"] = 'h8ip'
    return ip_dict
def get_mac():
    mac_dict = dict()
    mac_dict["h1"] = 'h1mac'
    mac_dict["h2"] = 'h2mac'
    mac_dict["h3"] = 'h3mac'
    mac_dict["h4"] = 'h4mac'
    mac_dict["h5"] = 'h5mac'
    mac_dict["h6"] = 'h6mac'
    mac_dict["h7"] = 'h7mac'
    mac_dict["h8"] = 'h8mac'
    return mac_dict
    
def get_links():
    command = "h1,s1 h2,s1 h3,s3 h4,s3 h5,s4 h6,s4 h6,s6 h8,s6" # level 1
    command += " s1,s2 s2,s3 s4,s5 s5,s6" #level 2
    command += " s2,s7 s7,s5" #level 3
    return command
    
    

    