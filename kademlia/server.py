#!/usr/bin/env python3

import socket 

mysocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

mysocket.bind(("0.0.0.0",12345))

while True:
    data, addr = mysocket.recvfrom(1024)
    print(data,addr)
