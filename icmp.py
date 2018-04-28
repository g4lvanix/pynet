#!/usr/bin/env python3

import struct
import time

class ICMPMessage:
    def __init__(self,mtype=0,code=0,header=None,payload=None,checksum=0):
        self.mtype      = mtype
        self.code       = code
        self.header     = header
        self.payload    = payload
        self.checksum   = checksum

        # if the checksum is 0 then it hasn't been calculated yet
        # i.e. the construtor has not been called with received data 
        # from the from_bytestring method
        if self.checksum == 0:
            self.checksum = self.calc_checksum()

    @classmethod
    def from_bytestring(cls, bytestring):
        (mtype, code, checksum, header) = struct.unpack(">BBHL",bytestring[:8])
        payload = bytestring[8:]
        return cls(mtype,code,header,payload,checksum)

    # calculate the checksum over the header and data
    def calc_checksum(self):
        bstr = self.encode()
        
        # pad the bytestring to even length
        if len(bstr)%2:
            bstr += bytes([0])

        # calculate 1's-complement sum over the integers
        cs = 0
        for i in struct.iter_unpack(">H",bstr):
            cs += i[0]
        cs = (cs & 0xFFFF) + (cs>>16)
        # return the 1's-complement of the sum i.e. invert all bits 
        return cs^0xFFFF

    # check wether or not the received and calculated checksum match
    def valid(self):
        return self.calc_checksum() == 0

    # return a bytes representation of this ICMP message
    def encode(self):
        tmp = struct.pack(">BBHL",self.mtype, self.code,
                                  self.checksum, self.header)
        tmp += self.payload

        return tmp

class ICMPEchoRequest(ICMPMessage):
    def __init__(self,ident,seqnum):
        header  = ((ident & 0xFFFF)<<16) | (seqnum & 0xFFFF)
        payload = struct.pack(">Q",int(time.time())) +  bytes(range(14,56))
        super().__init__(mtype=8,code=0,header=header,payload=payload)


class ICMPEchoReply(ICMPMessage):
    def __init__(self,request):
        pass
