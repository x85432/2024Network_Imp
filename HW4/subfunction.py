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
        theLSA = LSDB.get(theID, False)
        
        if theLSA is False:
            LSRList.append(theID)               # not in the LSDB
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
    
def sendLSU(LSApart, fromID):
    # LSApart = ["ID1", "ID2", ...]

    LSUpkt = "LSU|"
    for theID in LSApart:
        seq = LSDB[int(theID)]["seq"]
        # get ID and Seq
        LSUpkt += theID + "," + str(seq) + ","

        #link part
        linkdict = LSDB[int(theID)]["link"]
        for rID in linkdict:
            # routerID : cost
            LSUpkt += str(rID) + ":" + str(linkdict[rID]) + "_"
        LSUpkt = LSUpkt[0:-1] + "X" # kill the last _ , X for next theID 

    LSUpkt = LSUpkt[0:-1]
    if len(linkdict) == 0:
        LSUpkt += ','

    print(LSUpkt)
    send_msg(fromID, LSUpkt)

def processLSU(LSUpart):
    # LSUpart = ["ID,seq,(link)", "ID,seq,(link)"]
    # (link)  = "rID:cost_rID:cost_....rID:cost"
    for pkg in LSUpart:
        data = pkg.split(',') # 0:ID, 1:seq, 2:link
        theID    = data[0]
        theSeq   = data[1]
        linklist = data[2].split('_')

        linkdict = {}
        for alink in linklist:
            alinkData = alink.split(':')
            rID = int(alinkData[0])
            theCost = int(alinkData[1])
            linkdict[rID] = theCost

        theLSA = {"seq":int(theSeq), "link":linkdict}
        LSDB[int(theID)] = theLSA
def sendDBD(tarID):
    DBDpkt = "DBD|"
    for theID in LSDB:
        # print(LSDB[theID]["seq"])
        DBDpkt += str(theID)+":"+str(LSDB[theID]["seq"])+","

    DBDpkt = DBDpkt[0:-1]
    send_msg(tarID, DBDpkt)
