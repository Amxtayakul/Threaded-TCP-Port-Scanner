import socket

import sys
import time
import os

from datetime import datetime
#this will tell us the current date and time upon use 
#so that it can determine the time it took to scan our ports

#clear screen (cross-platform)
os.system('cls' if os.name == 'nt' else 'clear')

#ask input
remoteServer = input("Enter a remote host to scan: ")
remoteServerIP = socket.gethostbyname(remoteServer)

#decors and stuff
print ("_" * 60)
print ("Please wait, scanning remote host, remoteserverIP")
print ("_" * 60)

#check date and time
t1 = datetime.now()

#scan ports

try:
    for port in range(1,5000):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((remoteServerIP, port)) #we connect it into the port we entered
        if result == 0:
            print("Port {}:     open" .format(port))
        sock.close()

#error handlings        
except KeyboardInterrupt:
    print("You pressed 'Ctrl+C'")
    time.sleep(500)
    print("Exiting...")
    time.sleep(2000)
    sys.exit()
    
except socket.gaierror:
    print("Hostname could not be resolved.")
    time.sleep(500)
    print("Exiting...")
    time.sleep(2000)
    sys.exit()
    
except socket.error:
    print("Could not connect to a server")
    time.sleep(500)
    print("Exiting...")
    time.sleep(2000)
    sys.exit()
    
#check the date and time again
t2 = datetime.now()

#compute the time we scanned
total = t2 - t1
    
#print the information on the screen
print("Scanning completed in : ", total)