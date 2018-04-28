#!/usr/bin/env python3

import socket,random
import icmp


# open a IPv4 RAW socket
s = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.getprotobyname('icmp'))
# get our echo request 
er = icmp.ICMPEchoRequest(random.randint(0,2**16-1),0)
s.sendto(er.encode(),('8.8.8.8',80))

d = s.recv(1024)

response = icmp.ICMPMessage.from_bytestring(d)
print(response.valid())

print(d)
