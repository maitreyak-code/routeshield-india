"""Load the CAIDA AS-relationships file and print basic facts."""
import bz2
import sys
from collections import defaultdict
from pathlib import Path


def load(path):
    prov, cust, peer = defaultdict(set), defaultdict(set), defaultdict(set)
    with bz2.open(path, "rt") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            a, b, rel = line.split("|")[:3]
            a, b = int(a), int(b)
            if rel == "-1":          # a is provider of b
                cust[a].add(b)
                prov[b].add(a)
            elif rel == "0":         # peers
                peer[a].add(b)
                peer[b].add(a)
    return prov, cust, peer


if __name__ == "__main__":
    path = sorted(Path("data").glob("*.as-rel2.txt.bz2"))[-1]
    prov, cust, peer = load(path)
    ases = set(prov) | set(cust) | set(peer)
    print(f"File: {path.name}")
    print(f"Networks (ASes): {len(ases)}")
    print(f"Provider-customer links: {sum(len(v) for v in cust.values())}")
    print(f"Peering links: {sum(len(v) for v in peer.values()) // 2}")
    for a in (18101, 15412, 9498, 4755):
        print(f"AS{a}: providers={len(prov[a])} customers={len(cust[a])} peers={len(peer[a])}")