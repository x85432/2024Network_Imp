import socket
import sys
import threading
import time
import datetime

# TODO: To activate the OSPF router with Router ID = 1, use the following command: python ospf.py 1.

def printTime():
    now = datetime.datetime.now()
    print(now.strftime("<%H-%M-%S>"), end=" ")
        
def init(id, port):
    global ID, Port, neighbor_table, routing_table, LSDB

    ID = id
    Port = port
    neighbor_table = dict() # Router ID: {cost:c, state:s, DBD:list(d)}
    routing_table  = dict() # Router ID: [cost, next hop]
    LSDB           = dict() # Router ID: [Sequence, Links{Router ID: cost}]

  
def send_msg(tarID, msg):
    addr = ('0.0.0.0', 10000+int(tarID))
    s.sendto(msg.encode("utf-8"), addr)
    printTime()
    print(f"{ID} Send message {msg} to {tarID}")

def recv_msg():
    # print(f"Socket bound to port {port}")
    while True:
        # Receive data from the client
        print(f"{Port} Receiving...")
        data, addr = s.recvfrom(1024)
        decodedData = data.decode("utf-8")
        printTime()
        print(f"Received message: {decodedData} from port{addr[1]}")

def regular_send():
    while True:
        tarID = input("Input tarID:")
        msg   = input("Input message:")
        
        send_msg(tarID, msg)

if __name__ == '__main__':
    if len(sys.argv) != 2: 
        print("Number of Arguments is invalid.")
        sys.exit()
    
    inputID = sys.argv[1]
    port = 10000 + int(inputID)
  
    init(inputID, port)

    global s
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Bind the socket to the port
        s.bind(('', Port))       

        recv_thread = threading.Thread(target=recv_msg)
        recv_thread.start()

        send_thread = threading.Thread(target=regular_send)
        send_thread.start()
        
        recv_thread.join()
        send_thread.join()
        # while True:
        #     msg   = input("Msg(q to quit): ")
        #     if msg == 'q': break
        #     tarID = input("To            : ")

        #     send_msg(tarID, msg)
    

        s.close()