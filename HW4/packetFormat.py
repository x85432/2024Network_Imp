hello = "hello,no,src,srcID,dst,dstID"
print(hello.split(','))

ID = id
Port = port
neighbor_table = dict() # Router ID: {cost:c, state:s, DBD:dict(d)}
routing_table  = dict() # Router ID: [cost, next hop]
LSDB           = dict() # Router ID: {"seq":num, "link":{Router ID: cost}, "time":0]  #也就是存放LSA的地方
done           = False

LSU = "LSU|id,seq,(Link)ID1:cost1_ID2:cost2_...X ...|HH:MM:SS|srcID dstID"
rmLSU = "rmLSU|rmID|srcID dstID"