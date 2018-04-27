#!/usr/bin/env python3

import struct

class ICMPMessage:
    def __init__(self,mtype=0,code=0,header=None,payload=None,checksum=0):
        self.mtype      = mtype
        self.code       = code
        self.header     = header
        self.payload    = payload
        self.checksum   = checksum

        # we are probably being generated to be sent out 
        if self.checksum == 0:
            self.checksum = self.calc_checksum()

    @classmethod
    def from_bytestring(cls, bytestring):
        mtype   = bytestring[0]
        code    = bytestring[1]
        checksum= struct.unpack("!H",bytestring[2:4])[0]
        header  = struct.unpack("!L",bytestring[4:8])[0]
        payload = bytestring[8:].decode()
        return cls(mtype,code,header,payload,checksum)

    # calculate the checksum over the header and data
    def calc_checksum(self):
        pass

    # check wether or not the received and calculated checksum match
    def valid(self):
        return (self.calc_checksum() - self.checksum) == 0

    # return a bytestring representation of this ICMP message
    def encode(self):
        tmp = bytes([self.mtype, self.code])
        tmp += struct.pack("!H", self.checksum)
        tmp += struct.pack("!L", self.header)
        tmp += bytes(self.payload)
        return tmp

    

class ICMPEchoRequest(ICMPMessage):
    def __init__(self):
        super().__init__(t=0,c=0)
