#!/usr/bin/env python3

import random

def calc_ideal_peer_guid(guid,K):
    d = [2**r for r in range(0,K)]
    return [guid^b for b in d]

def calc_peer_distance(guid,guids):
    return [guid^g for g in guids]

if __name__ == "__main__":
    K = 32 
    guid = random.randrange(2**K)

    guids = calc_ideal_peer_guid(guid,K)

    print("Self:",guid)

    for g in guids:
        print(g)

    dists = calc_peer_distance(guid,guids)
    for d in dists:
        print(d)
