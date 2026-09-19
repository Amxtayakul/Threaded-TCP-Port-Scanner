import socket
import os
import sys
import time
import queue
import threading

from datetime import datetime
#this will tell us the current date and time upon use
#so that it can determine the time it took to scan our ports

#clear screen (cross-platform)
os.system('cls' if os.name == 'nt' else 'clear')

#banner - from https://coddy.tech/tools/ascii-art-generator
banner = r"""
█   █  █   █    ████    ███   ████  █████     ████   ███   ███   █   █  █   █  █████  ████    
██ ██░  █ █ ░   █░░░█  █ ░░█  █░░░█  ░█░░░░  █ ░░░░ █ ░░░ █ ░░█  ██  █░ ██  █░ █░░░░░ █░░░█   
█░█ █░░  █ ░ ░  ████░░ █░ ░█░ ████░░  █░░     ███░░ █░ ░░ █████░ █░█ █░ █░█ █░ ████░░ ████░░  
█░░░█░░  █░ ░   █░░░░  █░░ █░ █░░█░   █░░      ░░█  █░░   █░░░█░ █░░██░ █░░██░ █░░░░  █░░█░  
█░░ █░░  █░░    █░░     ███░  █░░░█░  █░░    ████░░  ███  █░░░█░ █░░ █░ █░░ █░ █████░ █░░░█░  
 ░░  ░░   ░░     ░░     ░░░   ░░   ░   ░░     ░░░░    ░░░  ░░  ░░ ░░  ░░ ░░  ░░ ░░░░░  ░░  ░ 
"""
print(banner)

#ask input
remoteServer = input("Enter a remote host to scan: ")
remoteServerIP = socket.gethostbyname(remoteServer)

#decors and stuff
print("_" * 60)
print("Please wait, scanning remote host", remoteServerIP)
print("_" * 60)

#check date and time
t1 = datetime.now()

#threading setup
portQueue = queue.Queue()
for port in range(1, 5000):
    portQueue.put(port)
 
printLock = threading.Lock()  #keeps our print statements from overlapping/garbling
 
def scanPort():
    while True:
        try:
            port = portQueue.get_nowait()
        except queue.Empty:
            return  # no more ports left, this worker is done
 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  #without this, closed/filtered ports can hang for a long time
        result = sock.connect_ex((remoteServerIP, port))  #we connect it into the port we entered
        if result == 0:
            with printLock:
                print("Port {}:     open".format(port))
        sock.close()
 
        portQueue.task_done()
 
#scan ports
try:
    numThreads = 100  #how many ports we check at the same time, feel free to tweak
    threads = []
    for _ in range(numThreads):
        t = threading.Thread(target=scanPort)
        t.daemon = True #so these die immediately when the main thread exits, no lingering
        t.start()
        threads.append(t)
 
    for t in threads:
        t.join()  #wait here until every thread has finished

#error handlings
except KeyboardInterrupt:
    print("You pressed 'Ctrl+C'")
    print("Exiting...")
    sys.exit()

except socket.gaierror:
    print("Hostname could not be resolved.")
    print("Exiting...")
    sys.exit()

except socket.error:
    print("Could not connect to a server")
    print("Exiting...")
    sys.exit()

# check the date and time again
t2 = datetime.now()

#compute the time we scanned
total = t2 - t1

#print the information on the screen
print("Scanning completed in : ", total)