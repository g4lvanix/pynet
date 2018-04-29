#!/usr/bin/env python3
import socket,json

req = {"rpc": "PING",
       "type": "REQ",
       "echo": "f7ff9e8b7bb2e09b70935a5d785e0cc5d9d0abf0",
       "id": "70c07ec18ef89c5309bbb0937f3a6342411e1fdd"}

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(("127.0.0.1",1234))
s.sendto(json.dumps(req).encode(),("127.0.0.1",5000))

d = s.recv(1024)

print(d)
