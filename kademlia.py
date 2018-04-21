#!/usr/bin/env python3

import asyncio,json
from collections import deque

# this sublass implements the transmission of RPC requsts to other Kademlia nodes
class KademliaRPCProtocol(asyncio.DatagramProtocol):
    def __init__(self,rpc):
        self.rpc = rpc

    def connection_made(self,transport):
        try:
            tmp = json.dumps(self.rpc).encode()
        except:
            print("Error serializing RPC request")
        else:
            transport.send_to(tmp)
        finally:
            transport.close()

# this subclass is used for listening for RPCs and replies from other Kademlia nodes
class KademliaListenProtocol(asyncio.DatagramProtocol):
    def __init__(self,request_queue,reply_queue):
        # request queue will have the pending requests appended to it
        self.request_queue = request_queue
        self.reply_queue = reply_queue

    def connection_made(self,transport):
        self.transport = transport
        print("Connected to socket")

    def datagram_received(self,data,addr):
        print(f"{data} received from {addr}")

        try:
            req = json.loads(data.decode())
        except:
            print("Error deserializing received data")
        else:
            tmp = {"addr": addr}

            if req.type == "REQ"
                self.request_queue.append({**addr, **req})
            elif req.type == "REP":
                self.reply_queue.append({**addr, **req})


class KademliaNode:
    def __init__(self,id,addr,event_loop,bucket_size=20,concurrency=3):
        self.id = id
        self.addr = addr
        self.event_loop = event_loop
        # queues requests received from other Kademlia nodes
        self.request_queue = deque()
        # queues replies received from other Kademlia nodes
        self.reply_queue = deque()
        # size of one k-bucket in the routing table
        self.bucket_size = bucket_size
        # concurrency parameter
        self.concurrency = concurrency

        # add the listener task to the event queue
        listener = self.event_loop.create_datagram_endpoint(
            lambda: KademliaListenProtocol(self.request_queue,self.reply_queue),
            local_addr=self.addr,
            reuse_addr=True,
            reuse_port=True)
        self.event_loop.ensure_future(listener)

        self.bootstrap()

    # kick off the bootstrap process of joining the network
    async def bootstrap(self):
        pass

    # work on entries in the request queue
    async def process_requests(self):
        pass

    # work on entries in the reply queue
    async def process_replies(self):
        pass

    # timer function that will ensure that the routing table will be refreshed
    # once every hour
    async def refresh_timer(self):
        while True:
            asyncio.sleep(3600)
            # TODO: kick off routing table refresh


if __name__ == "__main__":

    request_queue = deque()
    reply_queue = deque()

    loop = asyncio.get_event_loop()

    try:
        t = loop.create_datagram_endpoint(
                lambda: KademliaListenProtocol(request_queue,reply_queue),
                local_addr=("127.0.0.1",1234))
        loop.run_until_complete(t)
        loop.run_forever()

    finally:
        loop.stop()
