#!/usr/bin/env python3 

import asyncio
from collections import deque

global_message_queue = deque()

class ServerProtocol(asyncio.DatagramProtocol):

    def __init__(self,message_queue):
        self.message_queue = message_queue

    def connection_made(self,transport):
        self.transport = transport
        print("Connection made")

    def datagram_received(self,data,addr):
        self.message_queue.append({"addr": addr, "data": data})

async def process_message_queue(): 
    while True:
        try: 
            m = global_message_queue.popleft()
            print(m)
        except IndexError:
            pass

        await asyncio.sleep(0.01)


def main():
    loop = asyncio.get_event_loop()

    t = loop.create_datagram_endpoint(lambda: ServerProtocol(global_message_queue),
                                        local_addr=("127.0.0.1",1234))
    
    loop.create_task(t)
    loop.create_task(process_message_queue())

    print("Hello")
    try: 
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()


if __name__ == "__main__":
    main()
