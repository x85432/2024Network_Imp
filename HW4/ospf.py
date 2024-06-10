import socket
import sys
import threading
import time
import datetime
import heapq
import os
import traceback


# TODO: To activate the OSPF router with Router ID = 1, use the following command: python ospf.py 1.

""" message|others|src:srcID,dst:dstID """ # IP 一定要在最後
helloPKT = {"yes":"hello,yes", "no":"hello,no"}

def init(id, port):
    global ID, Port, neighbor_table, routing_table, LSDB, s, classicPKT
    ID = int(id)
    Port = port
    neighbor_table = dict() # Router ID: {cost:c, state:s, DBD:list(d)}
    routing_table  = dict() # Router ID: [cost, next hop]
    LSDB           = dict() # Router ID: [Sequence, Links{Router ID: cost}]  #也就是存放LSA的地方
    classicPKT = ["hello,yes", "hello,no", "DBD", "LSR", "LSU"]

def constructGraph():
    # print("now LSDB:\n", LSDB)
    graph = {fm: {} for fm in LSDB}
    
    print("now LSDB", LSDB)
    for fm in LSDB:
        linkdict = LSDB[fm]["link"]
        for to in linkdict:
            graph[fm][to] = int(linkdict[to]) 

    return graph

def dijkstra():
    def refreshTable(distances, next_hops):
        # distance = {node:cost}
        # next_hops = {node:next_hop}
        global routing_table # To change global value
        routing_table = {node: {} for node in distances}
        for node in distances:
            routing_table[node]["cost"]    = distances[node]
            routing_table[node]["nextHop"] = next_hops[node]

        # print(routing_table)

    # Dijkstra main
    graph = constructGraph()
    distances = {node: float('inf') for node in graph}
    next_hops = {node: None for node in graph}  # Initialize next hops to None
    par       = {node: None for node in graph}
    distances[ID] = 0
    queue = [(0, ID)]
    
    print("distance", distances)

    print("-"*5+"Dijk Start"+"-"*5)
    while queue:
        current_distance, current_node = heapq.heappop(queue) # src 到 currentNode 是最短的 (at this moment)
        print(current_node, "round:")
        if current_distance > distances[current_node]:
            continue
               
        for nei, wei in graph[current_node].items(): # 走過current_node的所有neighbors
            print(nei, wei)
            d = current_distance + wei
            
            if d < distances.get(nei):
                print(f"distance to {nei} change to {d}")
                distances[nei] = d
                par[nei] = current_node  # Update next hop
                print(f"{nei}'s next hop becomes {current_node}")

                heapq.heappush(queue, (d, nei))
    print("distance", distances)
    print("-"*5+"STOP"+"-"*5)


    for node in graph:
        if node == ID:
            # 自己的nextHop定為None
            # 如果neighbor的最後更新為"自己"，那就不要動它，因為確實要由我們forward pkt
            continue
        elif par[node] == ID:
            next_hops[node] = ID
            continue

        nextOfSrc = par[node]
        while nextOfSrc not in neighbor_table:
            nextOfSrc = par[nextOfSrc]
        next_hops[node] = nextOfSrc

    refreshTable(distances, next_hops)

    updatedID = []
    # Updated IDs
    for theID in distances:
        if theID == ID: continue
        if not routing_table.get(theID, False): # empty
            updatedID.append(str(theID))
        elif distances[theID] != routing_table[theID]["cost"]:
            updatedID.append(str(theID))

    if len(updatedID):
        print(updatedID)
        floodLSU(updatedID)

def printTime():
    now = datetime.datetime.now()
    print(now.strftime("<%H-%M-%S>"), end=" ")

def compareDBD(seqPart, fromID):
    # seqPart ["ID1:seq1","ID2:seq2" ...]
    LSRList = []
    compareDict = {}
    for _ in seqPart:
        aSeq = _.split(':')
        compareDict[int(aSeq[0])] = int(aSeq[1])
    
    for theID in compareDict:
        theLSA = LSDB.get(theID, False)         # missing will return False
        
        if theLSA is False:
            LSRList.append(theID)               # missing
            continue
        
        if compareDict[theID] > theLSA["seq"]: # value diff
            LSRList.append(theID)

    if len(LSRList) != 0:
        LSRpkt = "LSR|"
        for theID in LSRList:
            LSRpkt += str(theID) + ","
        LSRpkt = LSRpkt[0:-1]

        # print(LSRpkt)
        send_msg(fromID, LSRpkt)
        return False
    else:
        return True

def makeLSU(IDList):
    LSUpkt = "LSU|"
    for theID in IDList:
        seq = LSDB[int(theID)]["seq"]
        # get ID and Seq
        LSUpkt += theID + "," + str(seq) + ","

        #link part
        linkdict = LSDB[int(theID)]["link"]
        for rID in linkdict:
            # routerID : cost
            LSUpkt += str(rID) + ":" + str(linkdict[rID]) + "_"
        LSUpkt = LSUpkt[0:-1] + ","  # kill the last _

        if len(linkdict) == 0:
            LSUpkt += ','

        #time part
        theTime = LSDB[int(theID)]["time"]  # time format: HH:MM:SS
        LSUpkt += theTime

        LSUpkt += "X" # X for next theID 

        

    LSUpkt = LSUpkt[0:-1]  # take last char
    

    return LSUpkt

def sendLSU(LSApart, fromID):
    # LSApart = ["ID1", "ID2", ...]
    LSUpkt = makeLSU(LSApart)

    print(LSUpkt)
    send_msg(fromID, LSUpkt)

def processLSU(LSUpart):
    # LSUpart = ["ID,seq,(link)", "ID,seq,(link)"]
    # (link)  = "rID:cost_rID:cost_....rID:cost"
    updatedIDs = []
    for pkg in LSUpart:
        data = pkg.split(',') # 0:ID, 1:seq, 2:link
        theID    = data[0]
        theSeq   = data[1]
        
        print("DATA:", data)
        linklist = data[2].split('_')


        miss = LSDB.get(int(theID), True)           
        if miss is not True and int(theSeq) <= LSDB[int(theID)]["seq"]:   # we want new version or miss LSA only
            continue

        # 更新自己的資料
        linkdict = {}
        for alink in linklist:
            alinkData = alink.split(':')
            rID = int(alinkData[0])
            theCost = int(alinkData[1])
            linkdict[rID] = theCost

        now = datetime.datetime.now().strftime("%H:%M:%S")
        theLSA = {"seq":int(theSeq), "link":linkdict, "time":now}
        LSDB[int(theID)] = theLSA
        updatedIDs.append(theID)

        printTime()
        print(f"LSA {theID} updated to {theSeq}")


    if len(updatedIDs) != 0:
        floodLSU(updatedIDs)

        dijkstra()                 # re-compute SPF
    

def floodLSU(updatedIDs):
        for nei in neighbor_table:
            sendLSU(updatedIDs, nei)
            printTime()
            print("flood", updatedIDs, f"to {nei}") 

def updateDBD(seqPart, fromID):
    for p in seqPart:
        data = p.split(":")
        rID = data[0]
        seq = data[1]
        neighbor_table[fromID]["DBD"][int(rID)] = int(seq)

def sendDBD(tarID):
    DBDpkt = "DBD|"
    for theID in LSDB:
        # print(LSDB[theID]["seq"])
        DBDpkt += str(theID)+":"+str(LSDB[theID]["seq"])+","

    DBDpkt = DBDpkt[0:-1]
    send_msg(tarID, DBDpkt)

def send_msg(dstID, msg):
    # msg must be str
    IDmsg = msg
    if "src" not in msg or "dst" not in msg:
        IDmsg += "|src:"+str(ID)+",dst:"+str(dstID)

    # check = True # check dstID是否在routing_table中(可到達)
    # if dstID not in routing_table: 
    #     # 可能是table還沒更新，也可能tar根本不在connected的graph中
    #     if dstID is None:
    #         check = False  # self message
    #         print("Please don't whisper.")
    #     time.sleep(1)
    #     if dstID not in routing_table:
    #         check = False  # Drop


    messagePart = (msg.split("|"))[0]
    neiGood = False
    if int(dstID) in neighbor_table:
        if int(dstID) != ID and int(dstID) in routing_table: # dstID routing_table 一開始沒有
            linkCost = neighbor_table[int(dstID)]["cost"]
            routingCost = routing_table[int(dstID)]["cost"]
            nextHop     = routing_table[int(dstID)]["nextHop"]
            if (linkCost < routingCost) or (ID == nextHop): # compare routing and directly forward pkt
                neiGood = True

        else: neiGood = True

        if neiGood:
            try:
                addr = ('0.0.0.0', 10000+int(dstID))
                s.sendto(IDmsg.encode("utf-8"), addr)
            except Exception as e:
                print(e, "274行這裡")
                return 1

            # if messagePart not in classicPKT:
            printTime()
            print(f"Send {messagePart} to {dstID}")
    
    if neiGood is False:
        if int(dstID) in routing_table: # forward
            nextHop = routing_table.get(int(dstID))["nextHop"]
            print(dstID, "in the routing table and going to", nextHop)

            addr = ('0.0.0.0', 10000+int(nextHop))
            s.sendto(IDmsg.encode("utf-8"), addr)

            # if messagePart  not in classicPKT:
            printTime()
            print(f"Send {messagePart} to {nextHop} by {nextHop}")
        else:
            print(int(dstID), "not in the routing table.")
        
def recv_msg():
    # processData
    def processData(pkt, fromID):
        message = pkt[0].split(',')

        tmpState = neighbor_table[int(fromID)]["state"]
        if message[0] == "hello":
            if   message[1] == "yes": # Already receive "our hello"
                if   tmpState == "DOWN": neighbor_table[int(fromID)]["state"] = "EXCHANGE"
                elif tmpState == "INIT": neighbor_table[int(fromID)]["state"] = "EXCHANGE"
                elif tmpState == "FULL": sendDBD(fromID)
            elif message[1] == "no":  # NOT yet
                if   tmpState == "DOWN": neighbor_table[int(fromID)]["state"] = "INIT"

        elif message[0] == "DBD":
            seqPart = pkt[1].split(",")
            updateDBD(seqPart, fromID)
            check = compareDBD(seqPart, fromID) # compare DBD with LSDB
            if check is True:
                neighbor_table[int(fromID)]["state"] = "FULL"
                
        elif message[0] == "LSR":
            LSApart = pkt[1].split(",")
            sendLSU(LSApart, fromID)

        elif message[0] == "LSU":
            LSUpart = pkt[1].split("X")
            processLSU(LSUpart)

        elif message[0] == "rmLSU":
            rmID = int(pkt[1])
            rmlink(rmID)

        nowState = neighbor_table[int(fromID)]["state"]
        if tmpState != nowState:
            printTime()
            print(f"neighbor {fromID} state change from {tmpState} to {nowState}")

            if nowState == "FULL":
                sendDBD(fromID)
                

    # MAIN PART
    while True:
        # Receive data from the client
        try:
            data, addr = s.recvfrom(1024)
            fromID = addr[1] - 10000

            # Check to prevent thread crash down
            if int(fromID) not in neighbor_table:
                # print(f"{fromID} is not in the neighbor table.")
                # print(neighbor_table)
                continue
            
            # analyze data
            decodedData = data.decode("utf-8")
            pkt = decodedData.split('|')

            # print log
            """ message|others|src:srcID,dst:dstID """
            message     = pkt[0]        
            messagePart = pkt[0].split(',')
            IDpart      = pkt[-1].split(',')
            srcPart     = IDpart[0].split(':')
            srcID       = srcPart[1]
            dstPart     = IDpart[1].split(':')
            dstID       = dstPart[1]

            # processData to update table
            if int(dstID) == ID:
                # if message not in classicPKT:
                #     printTime()
                #     print(f"Recv message from {srcID}: {message}")

                printTime()
                print(f"Recv message from {srcID}: {message}")

                processData(pkt, fromID)
            else: # forwarding pkt
                if messagePart[0] != "hello":
                    printTime()
                    print(f"Forward message from {srcID} to {dstID}: {message}")
                    send_msg(dstID, decodedData)
                    # forwardPKT(decodedData, srcID, dstID)
        except socket.timeout:
            # timeout -> continue
            continue
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            break

# def forwardPKT(decodedData, srcID, dstID):
#     srcID, dstID = int(srcID), int(dstID)
#     # decodedData: message|others|src:srcID,dst:dstID
#     if not routing_table.get(dstID, False):
#         # no route or not yet receive information
#         print(f"There are no exist route for R{ID} that it is not able to forward pkt.")
#     else:
#         nextHop = routing_table[dstID]["nextHop"]
#         send_msg(nextHop, decodedData)

def rmlink(rmID):
    global neighbor_table, LSDB, routing_table
    if rmID != ID and (rmID in neighbor_table or rmID in LSDB):
        

        neighbor_table.pop(rmID, None)
        LSDB.pop(rmID, None)
        routing_table.pop(rmID, None)

        # link must delete
        myLink = LSDB[ID]["link"]
        myLink.pop(rmID, None)  
        
        for nei in neighbor_table: # all flood (first time remove)
            send_msg(nei, f"rmLSU|{rmID}")

        dijkstra()                 # re-compute SPF
                                   # will send updated distance to neighbors

def addlink(nID, cost):
    if int(nID) in neighbor_table:
        print(f"{nID} ALREADY IN!")
        return 0
    
    iniFormat = {"cost":cost, "state":"DOWN", "DBD":dict()}
    neighbor_table[int(nID)] = iniFormat
    LSDB[ID]["link"][int(nID)] = int(cost)

    nowTime = datetime.datetime.now().strftime("%H:%M:%S")
    LSDB[int(nID)] = {"seq":1, "link":{ID:int(cost)}, "time":nowTime}
    
    dijkstra()

def setlink(sID, newcost):
    neighbor_table[int(sID)]["cost"] = newcost
    LSDB[ID]["link"][int(sID)] = newcost

    floodLSU(updatedIDs=list(str(sID)))
    
    dijkstra()

def regularSend():
    while True:
        time.sleep(1)
        for nei in neighbor_table:
            neiState = neighbor_table[nei]["state"]
            if   neiState == "DOWN":
                send_msg(nei, helloPKT["no"])
            elif neiState == "INIT" or neiState == "EXCHANGE":
                send_msg(nei, helloPKT["yes"])

            ### Send DBD
            if neiState == "EXCHANGE":
                sendDBD(nei)

def LSAtimeout():
    def compareTime(timeYoung, timeOld):
            nowdate = datetime.datetime.now().date()
            complete_timeYoung_string = f"{nowdate} {timeYoung}"
            complete_timeOld_string   = f"{nowdate} {timeOld}"
            # restore time
            rTimeYoung = datetime.datetime.strptime(complete_timeYoung_string, "%Y-%m-%d %H:%M:%S")
            rTimeOld   = datetime.datetime.strptime(complete_timeOld_string, "%Y-%m-%d %H:%M:%S")

            diffTime = int((rTimeOld-rTimeYoung).total_seconds())
            return diffTime
    
    while True:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        # refresh self LSA
        time.sleep(15)

        LSDB[ID]["seq"] += 1   # seq ++
        LSDB[ID]["time"] = now # time refresh
        
        floodLSU(updatedIDs=list(str(ID)))

        newSeq = LSDB[ID]["seq"]
        printTime()
        print(f"LSA {ID} updated to {newSeq}")

        # scan self LSDB
        time.sleep(15)
        rm_list = []
        for nei in neighbor_table:
            getNei = LSDB.get(nei, False)
            while getNei is False: # until we addlink
                print(f"wait for {nei} addlink.")
                time.sleep(2)
                getNei = LSDB.get(nei, False)

            neiTime = getNei["time"]

            diffTime = compareTime(neiTime, now)
            if (diffTime > 30):
                printTime()
                print(f"{nei} TimedOut!")
                rm_list.append(nei)

        for nei in rm_list:
            rmlink(nei)

def showTable():
    print(f"R{ID} Neighbor Table:")
    print(neighbor_table)
    # for nei in neighbor_table:
    #     print(f"R{nei}", end= " ")
    #     print(neighbor_table[nei])

    print(f"R{ID} LSDB")
    print(LSDB)
    print(f"R{ID} Routing Table:")
    print(routing_table)

def CLI():
    while True:
        wrong = 0 
        command_line = input(">> ")
        command_list = command_line.strip().split(' ')
        
        if command_line.strip() =='exit':
            s.close()
            print("-"*5 + f"ShutDown Router{ID}" + "-"*5)
            
            return 0
        
        if command_line.strip() =='clear':
            os.system('clear')
            print("-"*5+f"Router {ID} command line interface"+"-"*5)
        
        elif len(command_list) == 2  and command_list[0] == 'rmlink': 
            wrong = rmlink(int(command_list[1]))
        elif len(command_list) == 3:
            if command_list[0] == 'addlink':
                neighbor_ID = command_list[1]
                cost        = command_list[2]
                wrong = addlink(neighbor_ID, int(cost))
            elif command_list[0] == 'setlink': #update cost
                neighbor_ID = command_list[1]
                cost        = command_list[2]
                wrong = setlink(neighbor_ID, int(cost))

            elif command_list[0] == 'send': #send message
                dst_ID = command_list[1]
                msg    = command_list[2]
                if "src" in msg or "dst" in msg: # invalid msg
                    wrong = 1
                    print("There some invalid message. (src or dst)")
                else:    
                    send_msg(dst_ID, msg)
        elif len(command_list) == 1 and command_list[0] == "showtable":
            showTable()
        else:
            wrong = 1
        if wrong == 1:
            print("Wrong command")

if __name__ == '__main__':
    if len(sys.argv) != 2: 
        print("Number of Arguments is invalid.")
        sys.exit()
    
    inputID = sys.argv[1]
    port = 10000 + int(inputID)
  
    init(inputID, port)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Bind the socket to the port
        s.bind(('', Port))       
        s.settimeout(1)
        
        # self LSA
        nowTime = datetime.datetime.now().strftime("%H:%M:%S")
        iniLSA = {"seq":1, "link":dict(), "time":nowTime}
        LSDB[ID] = iniLSA


        recv_thread = threading.Thread(target=recv_msg)
        recv_thread.start()

        send_thread = threading.Thread(target=regularSend, daemon=True)
        send_thread.start()

        LSA_timeout_thread = threading.Thread(target=LSAtimeout, daemon=True)
        LSA_timeout_thread.start()

        
        CLI()


# TODO: Hello, DBD, LSR, and LSU
# TODO: Command line interface
# TODO: display certain messages 