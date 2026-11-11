"""How does the June 2026 replay change if big networks already filter?"""
from pathlib import Path
from load_topology import load
from bgpsim import hijacked_share

path = sorted(Path("data").glob("*.as-rel2.txt.bz2"))[-1]
prov, cust, peer = (dict(x) for x in load(path))
ases = set(prov) | set(cust) | set(peer)
victim, attacker = 62041, 18101
skip = {15412, 9498, 4755, attacker, victim}
ranked = [a for a in sorted(ases, key=lambda a: -len(cust.get(a, ())))
          if a not in skip]


def share(rov):
    return hijacked_share(prov, cust, peer, ases, victim, attacker, rov)


print("Assume the N biggest networks (by customers) already filter:")
for n in (0, 20, 100, 500, 2000):
    bg = set(ranked[:n])
    print(f"N={n:>4}: nobody else {share(bg):.1%} | + FLAG {share(bg | {15412}):.1%}"
          f" | + FLAG, Airtel, Tata {share(bg | {15412, 9498, 4755}):.1%}", flush=True)