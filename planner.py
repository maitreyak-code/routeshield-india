"""Greedy ROV planner on the real map, scored on HELD-OUT scenarios.
ASSUMPTIONS: candidates = top 150 Indian transit networks by customers;
lazy greedy (assumes diminishing returns; a heuristic, no guarantee)."""
import heapq
import random
import statistics
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from bgpsim import simulate
from scenarios import build

CAND, K = 150, 8
KS = (1, 2, 3, 5, 8)

prov, cust, peer, ases, india, train, test = build()
N = len(ases) - 2


def infected(victim, attacker, rov):
    res = simulate(prov, cust, peer, victim, attacker, rov)
    return {n for n, o in res.items() if o == attacker and n not in (victim, attacker)}


def avg_share(rov, scenarios):
    return statistics.mean(len(infected(v, a, rov)) / N for v, a in scenarios)


def cone_size(n):
    seen, stack = {n}, [n]
    while stack:
        x = stack.pop()
        for c in cust.get(x, ()):
            if c not in seen:
                seen.add(c)
                stack.append(c)
    return len(seen)


def greedy(cands, k, scenarios):
    chosen, cache = [], {}
    cur = [infected(v, a, set()) for v, a in scenarios]

    def gain(c):
        rov = set(chosen) | {c}
        g, new = 0, {}
        for i, (v, a) in enumerate(scenarios):
            if c in cur[i]:               # only matters if the hijack reaches c
                s = infected(v, a, rov)
                new[i] = s
                g += len(cur[i]) - len(s)
        cache[c] = new
        return g

    heap = [(-gain(c), c, 0) for c in cands]
    heapq.heapify(heap)
    for rnd in range(k):
        while True:
            negg, c, r = heapq.heappop(heap)
            if r == rnd:
                break
            heapq.heappush(heap, (-gain(c), c, rnd))
        chosen.append(c)
        for i, s in cache[c].items():
            cur[i] = s
        print(f"  pick {rnd + 1}: AS{c} (customers={len(cust[c])})", flush=True)
    return chosen


def curve(order, scenarios):
    return [avg_share(set(order[:k]), scenarios) for k in KS]


if __name__ == "__main__":
    transit = sorted((a for a in india if cust.get(a)), key=lambda a: -len(cust[a]))
    cands = transit[:CAND]
    t0 = time.time()
    print(f"Training greedy on {len(train)} scenarios, {len(cands)} candidates...")
    order = greedy(cands, K, train)
    print(f"Greedy done in {time.time() - t0:.0f}s. Scoring on held-out scenarios...")
    none = avg_share(set(), test)
    g = curve(order, test)
    cu = curve(cands, test)
    cones = sorted(cands, key=lambda a: -cone_size(a))
    co = curve(cones, test)
    rng = random.Random(1)
    rs = [curve(rng.sample(cands, K), test) for _ in range(3)]
    r = [statistics.mean(x) for x in zip(*rs)]
    print(f"\nNo extra ROV: {none:.1%}")
    for i, k in enumerate(KS):
        print(f"k={k}: greedy {g[i]:.1%} | cone {co[i]:.1%} | "
              f"customers {cu[i]:.1%} | random {r[i]:.1%}")
    plt.figure(figsize=(7, 4.2))
    xs = [0] + list(KS)
    for name, cv, st in (("Greedy planner", g, "-o"), ("Biggest customer cone", co, "--s"),
                         ("Most customers", cu, ":^"), ("Random (avg of 3)", r, "-.x")):
        plt.plot(xs, [none] + cv, st, label=name)
    plt.xlabel("Indian networks enabling ROV (k)")
    plt.ylabel("Avg share of networks hijacked (held-out)")
    plt.title("Real map: which Indian networks should check first?")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("planner_results.png", dpi=150)
    print("Saved planner_results.png")