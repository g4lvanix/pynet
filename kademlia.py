#!/usr/bin/env python3

import socket

class client:
    def __init__(self,ID,ipaddr,port,k=20):

        self.info = (ID,ipaddr,port)

        print("client instantiated")

class kbucket:
    def __init__(self,k):
        self.k = k
