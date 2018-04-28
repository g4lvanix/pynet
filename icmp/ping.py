#!/usr/bin/env python3

import socket,random
import icmp
import time 

# open a IPv4 RAW socket
s = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.getprotobyname('icmp'))
# get our echo request 

try:
    while True:
        er = icmp.ICMPEchoRequest(random.randint(0,2**16-1),0)
        s.sendto(er.encode(),('192.168.1.199',0))
        d = s.recv(1024)
        response = icmp.ICMPMessage.from_bytes(d)

        print(response.valid())
        time.sleep(1)

except KeyboardInterrupt:
    s.close()
