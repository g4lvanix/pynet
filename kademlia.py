#!/usr/bin/env python3

import asyncio,json
from collections import deque
import time

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
    def __init__(self,message_queue):
        # message queue will have the pending requests appended to it
        self.message_queue = message_queue

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
            self.message_queue.append({**addr, **req})

# class that stores peer information such as ID, address and alive status
# which is important for updating the routing table
class KademliaPeer:
    def __init__(self,id,addr,alive=True):
        self.id = id
        self.addr = addr
        self.alive = alive

    # ping this node to see if it is still alive
    async def ping(self):
        pass

    # send a find_node rpc to this node
    async def find_node(self,id):
        pass

    # send a find_value rpc to this node
    async def find_value(self,value):
        await self.find_node(id)

    # send a store RPC to this node
    async def store(self,key,value):
        pass

class KademliaKBucket:
    def __init__(self,bucket_size=20):
        # size of one k-bucket in the routing table
        self.bucket_size = bucket_size
        # initialize k buckets
        self.kbuckets = [deque(maxlen=self.bucket_size) for i in range(160)]
        # remember when we last performed a node lookup in the ith bucket
        self.lookup_times = [0 for i in range(160)]

    # calculate the index in the kbucket list which is the position of
    # the most significant bit in the binary representation of the id
    # this relies on the bin() function not returning leading zeros
    def id_to_bucket(self,id):
        return len(bin(int(id,16))[2:])-1

    # find the KademliaPeer object with the given id in the k buckets
    def find_peer(self,id):
        bucket_index = self.id_to_bucket(id)

        try:
            peer = [p for p in self.kbuckets[bucket_index] if p.id == id][0]
        except IndexError:
            return None
        else:
            return peer

    # update the appropriate kbucket using the given KademliaPeer object
    async def update_kbucket(self,peer):
        bucket_index = self.id_to_bucket(peer.id)

        if peer in self.kbuckets[bucket_index]:
            self.kbuckets[bucket_index].remove(peer)
            self.kbuckets[bucket_index].append(peer)

        elif self.kbuckets[bucket_index].size() < self.bucket_size:
            self.kbuckets[bucket_index].append(peer)

        else:
            # ping the least recently seen node == first node in the deque
            lrs_peer = self.kbuckets[bucket_index].popleft()
            await lrs_peer.ping()

            if lrs_peer.alive:
                self.kbuckets[bucket_index].append(lrs_peer)
            else:
                self.kbuckets[bucket_index].append(peer)

class KademliaNode:
    def __init__(self,id,addr,event_loop,bucket_size=20,concurrency=3):
        self.id = id
        self.addr = addr
        self.event_loop = event_loop
        # queues messages received from other Kademlia nodes
        self.message_queue = deque()
        # concurrency parameter
        self.concurrency = concurrency

        self.routing_table = KademliaKBucket(bucket_size=bucket_size)

        # add the listener task to the event queue
        listener = self.event_loop.create_datagram_endpoint(
            lambda: KademliaListenProtocol(self.message_queue),
            local_addr=self.addr,
            reuse_addr=True,
            reuse_port=True)
        self.event_loop.ensure_future(listener)

        # initially we're not bootstrapped, user has to kick off the
        # bootstrap procedure by registering that task with the event loop
        self.bootstrapped = False

    # kick off the bootstrap process of joining the network
    async def bootstrap(self):
        pass

    # work on entries in the request queue
    async def process_message_queue(self):
        pass

    # timer function that will ensure that the routing table will be refreshed
    # once every hour
    async def refresh_timer(self):
        while True:
            asyncio.sleep(3600)
            # TODO: kick off routing table refresh

    # calculate the Kademlia distance metric given two id strings
    def distance(self,id1,id2):
        return int(id1,16) ^ int(id2,16)

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
