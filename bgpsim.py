"""Simplified Gao-Rexford route propagation on the real CAIDA AS graph."""
import heapq
from pathlib import Path
from load_topology import load


def better(new, old):
    if old is None:
        return True
    if new[0] != old[0]:
        return new[0] > old[0]
    if new[1] != old[1]:
        return new[1] < old[1]
    return new[2] < old[2]


def simulate(prov, cust, peer, victim, attacker, rov):
    """Return dict node -> origin it ends up routing towards."""
    best = {victim: (4, 0, victim, victim), attacker: (4, 0, attacker, attacker)}

    def offer(node, route):
        if node in rov and route[3] == attacker:
            return False
        if better(route, best.get(node)):
            best[node] = route
            return True
        return False

    heap = [(0, victim), (0, attacker)]
    heapq.heapify(heap)
    while heap:
        ln, n = heapq.heappop(heap)
        r = best[n]
        if r[1] != ln or r[0] not in (3, 4):
            continue
        for p in prov.get(n, ()):
            if offer(p, (3, ln + 1, n, r[3])):
                heapq.heappush(heap, (ln + 1, p))
    for n, r in [(n, r) for n, r in best.items() if r[0] in (3, 4)]:
        for q in peer.get(n, ()):
            offer(q, (2, r[1] + 1, n, r[3]))
    heap = [(best[n][1], n) for n in best]
    heapq.heapify(heap)
    while heap:
        ln, n = heapq.heappop(heap)
        r = best[n]
        if r[1] != ln:
            continue
        for c in cust.get(n, ()):
            if offer(c, (1, ln + 1, n, r[3])):
                heapq.heappush(heap, (ln + 1, c))
    return {n: r[3] for n, r in best.items()}


def hijacked_share(prov, cust, peer, ases, victim, attacker, rov):
    res = simulate(prov, cust, peer, victim, attacker, rov)
    others = [n for n in ases if n not in (victim, attacker)]
    return sum(1 for n in others if res.get(n) == attacker) / len(others)


if __name__ == "__main__":
    path = sorted(Path("data").glob("*.as-rel2.txt.bz2"))[-1]
    prov, cust, peer = (dict(x) for x in load(path))
    ases = set(prov) | set(cust) | set(peer)
    victim, attacker = 62041, 18101      # Telegram, Rcom
    cases = [("No ROV anywhere", set()),
             ("Only AS15412 (FLAG) checks", {15412}),
             ("Only AS9498 + AS4755 check", {9498, 4755}),
             ("AS15412 + AS9498 + AS4755 check", {15412, 9498, 4755})]
    for name, rov in cases:
        s = hijacked_share(prov, cust, peer, ases, victim, attacker, rov)
        print(f"{name}: hijack reaches {s:.1%} of networks")