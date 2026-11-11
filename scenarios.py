"""Reproducible hijack scenarios: (victim, attacker) pairs on the real map.
ASSUMPTIONS: victims = random Indian stub networks (stand-in for critical
services; no verified list); attackers = random Indian networks."""
import random
from pathlib import Path
from load_topology import load
from download_apnic import indian_asns


def build(seed=7, n_train=30, n_test=30):
    path = sorted(Path("data").glob("*.as-rel2.txt.bz2"))[-1]
    prov, cust, peer = (dict(x) for x in load(path))
    ases = set(prov) | set(cust) | set(peer)
    india = indian_asns(Path("data") / "delegated-apnic-latest.txt") & ases
    stubs = sorted(a for a in india if not cust.get(a))
    attackers = sorted(india)
    rng = random.Random(seed)
    seen = set()

    def make(n):
        out = []
        while len(out) < n:
            pair = (rng.choice(stubs), rng.choice(attackers))
            if pair[0] != pair[1] and pair not in seen:
                seen.add(pair)
                out.append(pair)
        return out

    train = make(n_train)
    test = make(n_test)          # held-out: never seen by the planner
    return prov, cust, peer, ases, india, train, test


if __name__ == "__main__":
    *_, india, train, test = build()
    print(f"Indian networks in map: {len(india)}")
    print(f"Train scenarios: {len(train)}, held-out test scenarios: {len(test)}")
    print("First 3 train (victim, attacker):", train[:3])
