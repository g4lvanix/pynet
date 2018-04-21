#!/usr/bin/env python3

import asyncio,json
from collections import deque
import time,random

'''
Messages passed between nodes are simply Python dictionaries that are
serialized to JSON.

Every RPC request contains the following fields:

    rpc: string, possible values are "PING", "FIND_NODE", "FIND_VALUE", "STORE"
    type: "REQ"
    echo: random 160 bit value encoded as hex string, needs to be echoed back in reply

    Additional fields for PING: None
    Additional fields for FIND_NODE: id: string, 160 bit node id as hex string
    Additional fields for FIND_VALUE: key: string, 160 bit key as hex string
    Additional fields for STORE: key: string, 160 bit key as hex string
                                 val: string, 160 bit key as hex string

Every RPC reply contains the following fields:

    rpc and echo as above

    type: "REP"

    Additional fields for PING: None
    Additional fields for FIND_NODE: nodes: list of tuples with ("address",port) pairs

    Additional fields for FIND_VALUE: if key/val not on this node:
                                        nodes: list of tuples with ("address",port) pairs
                                      else:
                                          value: the stored value

    Additional fields for STORE: None
'''

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
    def __init__(self,id,addr,event_loop,alive=True,timeout=5):
        self.id = id
        self.addr = addr
        self.event_loop = event_loop
        self.alive = alive
        # timeout after which the peer is considered dead after sending a request
        self.timeout = 5

        # this property is set by the KademliaNode class when it finds a response
        # from this peer in the incoming message queue
        self.response = None
        # the expected random echo value
        self.expected_echo = None

    # launch a generic request
    async def generic_request(self,req):

        conn = self.event_loop.create_datagram_endpoint(
            lambda: KademliaRPCProtocol(req),
            local_addr=self.addr,
            reuse_port=True)

        await self.event_loop.ensure_future(conn)

        t_start = time.now()

        while self.response == None or self.response.echo != self.expected_echo:
            while (time.now() - t_start) < self.timeout:
                yield
            else:
                return None
        else:
            return self.response

    # ping this node to see if it is still alive
    async def ping(self):
        self.expected_echo = hex(random.randint(0,2**160-1))

        req = { "rpc": "PING", "type": "REQ",
                "echo": self.expected_echo}

        await rep = self.generic_request(req)

        # if the reply is a None object then the node timed out or responded
        # with an incorrect echo
        self.alive = rep != None

        self.response = None
        return

    # send a find_node rpc to this node
    async def find_node(self,id):
        self.expected_echo = hex(random.randint(0,2**160-1))

        req = { "rpc": "FIND_NODE", "type": "REQ",
                "echo": self.expected_echo,
                "id": id}

        await rep = self.generic_request(req)

        if rep != None:
            tmp = self.response.nodes
            self.response = None
            return tmp
        else:
            return None

    # send a find_value rpc to this node
    async def find_value(self,key):
        self.expected_echo = hex(random.randint(0,2**160-1))

        req = { "rpc": "FIND_VALUE", "type": "REQ",
                "echo": self.expected_echo,
                "key": key}

        await rep = self.generic_request(req)

        if rep != None:

            try:
                tmp = self.response.value
            except KeyError:
                tmp = self.response.nodes
            finally:
                self.response = None

            return tmp

        else:
            return None

    # send a store RPC to this node
    async def store(self,key,value):
        self.expected_echo = hex(random.randint(0,2**160-1))

        req = { "rpc": "STORE", "type": "REQ",
                "echo": self.expected_echo,
                "key": key,
                "value": value}

        await rep = self.generic_request(req)

        self.response = None
        return

class KademliaKBucket:
    def __init__(self,event_loop,bucket_size=20):
        self.event_loop = event_loop
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

        # calculate the Kademlia distance metric given two id strings
        def distance(self,id1,id2):
            return int(id1,16) ^ int(id2,16)

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

    # work on the incoming message queue
    async def process_message_queue(self):
        pass

if __name__ == "__main__":

    loop = asyncio.get_event_loop()

    try:
        kn = KademliaNode(id='2ef7bde608ce5404e97d5f042f95f89f1c232871',
                          addr=('127.0.0.1',5000),
                          event_loop=loop)
        loop.run_until_complete(kn.bootstrap())
        loop.run_forever()

    finally:
        loop.stop()
