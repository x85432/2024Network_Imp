import socket
import sys

# TODO: To activate the OSPF router with Router ID = 1, use the following command: python ospf.py 1.

if __name__ == '__main__':
    ID=0
    if len(sys.argv) != 2: 
        print("Number of Arguments is invalid.")
        sys.exit()
    

    ID = sys.argv[1]
    print("ID =", ID)

    port = 10000 + int(ID)
    #                  IPv4            UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Bind the socket to the port
        s.bind(('', port))
        
        print(f"Socket bound to port {port}")

        to_ID = input("輸入ID:")
        addr = ('0.0.0.0', 10000+int(to_ID))
        test = "test"
        s.sendto(test.encode("utf-8"), addr)

        while True:
            # Receive data from the client
            data, addr = s.recvfrom(1024)
            decodedData = data.decode("utf-8")
            print(f"Received message: {decodedData} from {addr}")

            # Send a response back to the client
            response = "Message received!"

            to_ID = input("輸入ID:")
            addr = ('0.0.0.0', 10000+int(to_ID))
            s.sendto(response.encode(), addr)
	

# TODO: Hello, DBD, LSR, and LSU
# TODO: Command line interface
# TODO: display certain messages 