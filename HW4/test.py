import socket
import sys
import threading

def is_socket_open(s):
    try:
        # 检查套接字是否已关闭
        s.fileno()
        return True  # 套接字尚未关闭
    except socket.error:
        return False  # 套接字已关闭

def recv_msg():    
    global s
    while is_socket_open(s):
        s.recvfrom(1024)

    print("已經跳脫了")

    
def CLI():
    while True:
        wrong = 0 
        command_line = input(">> ")
        command_list = command_line.strip().split(' ')
        
        if command_line.strip() =='exit':
           
            s.close()
            print("Don't press anything to wait program shutdown. Thank Q.")
            
            return 0
        
       
if __name__ == '__main__':
    if len(sys.argv) != 2: 
        print("Number of Arguments is invalid.")
        sys.exit()
    
    inputID = sys.argv[1]
    port = 10000 + int(inputID)
  
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Bind the socket to the port
        s.bind(('', port))       


        recv_thread = threading.Thread(target=recv_msg, daemon=True)
        recv_thread.start()

        

        
        CLI()

        recv_thread.join()

