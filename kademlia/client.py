#!/usr/bin/env python3

import socket

mysocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

mysocket.bind(("127.0.0.1",23456))

mysocket.sendto(b"Hello",("127.0.0.1",12345))
