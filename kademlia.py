#!/usr/bin/env python3

import asyncio,json
from collections import deque

class KademliaSendRPC(asyncio.DatagramProtocol):
    def __init__(self,rpc):
        self.rpc = rpc

    def connection_made(self,transport):
        transport.send_to(json.dumps(self.rpc).encode())
        transport.close()

# this subclass is used for listening for RPCs from other Kademlia nodes
class KademliaListen(asyncio.DatagramProtocol):
    def __init__(self,request_queue):
        # request queue will have the pending requests appended to it
        self.request_queue = request_queue

    def connection_made(self,transport):
        self.transport = transport
        print("Connected to socket")

    def datagram_received(self,data,addr):
        print(f"{data} received from {addr}")

        try:
            req = json.loads(data.decode())
        except:
            print("Invalid request received")
        else:
            tmp = {"addr": addr}
            request_queue.append({**addr, **req})


class KademliaNode:
    def __init__(self,id,addr,event_loop,k=20,alpha=3):
        self.id = id
        self.addr = addr
        self.event_loop = event_loop
        self.request_queue = deque()
        # size of one k-bucket in the routing table
        self.k = k
        # concurrency parameter
        self.alpha = alpha

        # add the listener task to the event queue
        listener = self.event_loop.create_datagram_endpoint(
            lambda: KademliaListen(self.request_queue),
            local_addr=self.addr,
            reuse_addr=True,
            reuse_port=True)
        self.event_loop.ensure_future(listener)

        self.bootstrap()

    # kick off the bootstrap process of joining the network
    async def bootstrap(self):
        pass

    # work on entries in the request queue
    async def serve_requests(self):
        pass

    # timer function that will ensure that the routing table will be refreshed
    # once every hour
    async def refresh_timer(self):
        while True:
            asyncio.sleep(3600)
            # TODO: kick off routing table refresh


if __name__ == "__main__":

    requeue = deque()

    loop = asyncio.get_event_loop()

    try:
        t = loop.create_datagram_endpoint(
                lambda: KademliaListen(requeue),
                local_addr=("127.0.0.1",1234))
        loop.run_until_complete(t)
        loop.run_forever()

    finally:
        loop.stop()
