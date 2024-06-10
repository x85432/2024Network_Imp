import threading
import time

done = False
global y
y = 0
def worker(text):
    global y
    while not done:
        x = int(input("input x:"))
        if x == 1: 
            y = 2

def worker2():
    while y!=2:
        time.sleep(1)
        print(f"y={y} now")
        print("wait y = 2")
    print("y = 2 now")
t1 = threading.Thread(target=worker, daemon=True, args=("AAA",))
t2 = threading.Thread(target=worker2)
t1.start()
t2.start()
input("press enter to stop")
print(y)
print()
# done = True



