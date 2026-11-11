"""
RouteShield toy: a SYNTHETIC mini-internet to show the idea end to end.
NOT real India data. It demonstrates the pipeline you would later feed real data into.

What it does
  1. Builds a made-up AS graph (tier-1 core, tier-2 transit, stub networks).
  2. Simulates a prefix hijack with simplified Gao-Rexford routing rules.
  3. Lets "ROV" networks drop routes from the attacker (the signed-registry check).
  4. Replays an "incident": a stub with one upstream hijacks a victim.
  5. Greedy planner picks which Indian-labelled networks should enable ROV,
     compared with random / highest-degree / biggest-customer-cone baselines.

Simplifications (say these out loud): exact-prefix hijack only, one prefix,
no sub-prefix hijacks, no ASPA, ties broken by lowest neighbour ID.
Run:  python3 toy_sim.py
"""
import heapq
import random
import statistics
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 7
rng = random.Random(SEED)

# ---------- 1. build a synthetic internet ----------
N_T1, N_T2, N_STUB = 5, 40, 220
prov = {}   # node -> set of providers
cust = {}   # node -> set of customers
peer = {}   # node -> set of peers
tier = {}
country = {}


def add(n, t):
    prov[n], cust[n], peer[n] = set(), set(), set()
    tier[n] = t


def link_cp(c, p):
    prov[c].add(p)
    cust[p].add(c)


def link_peer(a, b):
    peer[a].add(b)
    peer[b].add(a)


t1 = list(range(N_T1))
t2 = list(range(N_T1, N_T1 + N_T2))
stubs = list(range(N_T1 + N_T2, N_T1 + N_T2 + N_STUB))
for n in t1:
    add(n, 1)
for n in t2:
    add(n, 2)
for n in stubs:
    add(n, 3)
for i in t1:
    for j in t1:
        if i < j:
            link_peer(i, j)
for n in t2:
    for p in rng.sample(t1, 2):
        link_cp(n, p)
for _ in range(60):
    a, b = rng.sample(t2, 2)
    if b not in peer[a] and b not in prov[a] and a not in prov[b]:
        link_peer(a, b)
for n in stubs:
    k = 1 if rng.random() < 0.6 else 2          # many stubs are single-homed
    for p in rng.sample(t2, k):
        link_cp(n, p)

ALL = t1 + t2 + stubs
# label ~30% of transit + stubs as "India"
IN = set(rng.sample(t2, 14)) | set(rng.sample(stubs, 70))
for n in ALL:
    country[n] = "IN" if n in IN else "XX"
CRITICAL = rng.sample(sorted(IN & set(stubs)), 10)   # e.g. banks/UPI/gov origins


# ---------- 2. routing with simplified Gao-Rexford ----------
# route = (rank, pathlen, nexthop, origin); higher rank wins (customer=3, peer=2, provider=1)
def better(new, old):
    if old is None:
        return True
    if new[0] != old[0]:
        return new[0] > old[0]
    if new[1] != old[1]:
        return new[1] < old[1]
    return new[2] < old[2]


def simulate(victim, attacker, rov):
    """Return dict node -> origin it ends up routing towards."""
    best = {}
    for o in (victim, attacker):
        best[o] = (4, 0, o, o)

    def offer(node, route):
        # ROV: drop the attacker's origin (the signed record says only victim may originate)
        if node in rov and route[3] == attacker:
            return False
        if better(route, best.get(node)):
            best[node] = route
            return True
        return False

    # phase 1: customer -> provider (routes learned from customers)
    heap = [(0, o) for o in (victim, attacker)]
    heapq.heapify(heap)
    while heap:
        ln, n = heapq.heappop(heap)
        r = best[n]
        if r[1] != ln or r[0] not in (3, 4):
            continue
        for p in prov[n]:
            if offer(p, (3, ln + 1, n, r[3])):
                heapq.heappush(heap, (ln + 1, p))
    # phase 2: one hop across peers (only customer-learned routes are exported)
    snapshot = [(n, r) for n, r in best.items() if r[0] in (3, 4)]
    for n, r in snapshot:
        for q in peer[n]:
            offer(q, (2, r[1] + 1, n, r[3]))
    # phase 3: provider -> customer (everything is exported to customers)
    heap = [(best[n][1], n) for n in best]
    heapq.heapify(heap)
    while heap:
        ln, n = heapq.heappop(heap)
        r = best[n]
        if r[1] != ln:
            continue
        for c in cust[n]:
            if offer(c, (1, ln + 1, n, r[3])):
                heapq.heappush(heap, (ln + 1, c))
    return {n: r[3] for n, r in best.items()}


def hijacked_share(victim, attacker, rov):
    res = simulate(victim, attacker, rov)
    others = [n for n in ALL if n not in (victim, attacker)]
    bad = sum(1 for n in others if res.get(n) == attacker)
    return bad / len(others)


# ---------- 3. incident replay (analogue of the June 2026 event) ----------
def incident_replay():
    # attacker: an Indian stub with a single upstream; victim: a foreign stub
    cands = [s for s in stubs if s in IN and len(prov[s]) == 1]
    attacker = cands[0]
    victim = next(s for s in stubs if s not in IN)
    upstream = next(iter(prov[attacker]))
    base = hijacked_share(victim, attacker, set())
    with_up = hijacked_share(victim, attacker, {upstream})
    return attacker, upstream, victim, base, with_up


# ---------- 4. planner ----------
def make_scenarios(n=50):
    sc = []
    for _ in range(n):
        v = rng.choice(CRITICAL)
        a = rng.choice([x for x in ALL if x != v])
        sc.append((v, a))
    return sc


def avg_hijack(rov, scenarios):
    return statistics.mean(hijacked_share(v, a, rov) for v, a in scenarios)


def cone_size(n):
    seen, stack = {n}, [n]
    while stack:
        x = stack.pop()
        for c in cust[x]:
            if c not in seen:
                seen.add(c)
                stack.append(c)
    return len(seen)


def greedy(cands, k, scenarios):
    chosen, curve, order = set(), [], []
    for _ in range(k):
        best_c, best_v = None, None
        for c in cands:
            if c in chosen:
                continue
            v = avg_hijack(chosen | {c}, scenarios)
            if best_v is None or v < best_v:
                best_c, best_v = c, v
        chosen.add(best_c)
        order.append(best_c)
        curve.append(best_v)
    return order, curve


def curve_for(order, scenarios):
    return [avg_hijack(set(order[:i]), scenarios) for i in range(1, len(order) + 1)]


if __name__ == "__main__":
    print(f"Synthetic internet: {len(ALL)} networks, {len(IN)} labelled 'India', "
          f"{len(CRITICAL)} critical origins")

    a, up, v, base, with_up = incident_replay()
    print("\n--- Incident replay (toy analogue of 16 June 2026) ---")
    print(f"Attacker AS{a} (single upstream AS{up}) hijacks victim AS{v}")
    print(f"Hijack reaches {base:.1%} of networks with no ROV anywhere")
    print(f"Hijack reaches {with_up:.1%} if ONLY its upstream AS{up} enables ROV")

    K = 8
    scen = make_scenarios(50)          # training scenarios: the planner sees these
    test = make_scenarios(50)          # held-out scenarios: used for ALL reported numbers
    cands = sorted(n for n in IN if tier[n] in (1, 2, 3))
    cands = sorted(cands, key=lambda n: -len(cust[n]) )[:30]   # shortlist: top 30 by customers
    none = avg_hijack(set(), test)
    chosen, _train_curve = greedy(cands, K, scen)
    g_curve = curve_for(chosen, test)
    deg_order = sorted(cands, key=lambda n: -(len(cust[n]) + len(peer[n]) + len(prov[n])))
    cone_order = sorted(cands, key=lambda n: -cone_size(n))
    d_curve = curve_for(deg_order[:K], test)
    c_curve = curve_for(cone_order[:K], test)
    r_curves = []
    for _ in range(5):
        r_curves.append(curve_for(rng.sample(cands, K), test))
    r_curve = [statistics.mean(x) for x in zip(*r_curves)]

    print("\n--- Planner (average over 50 held-out random hijacks of critical origins) ---")
    print(f"No ROV:            {none:.1%}")
    for i in (1, 3, 5, K):
        print(f"k={i}: greedy {g_curve[i-1]:.1%} | cone {c_curve[i-1]:.1%} | "
              f"degree {d_curve[i-1]:.1%} | random {r_curve[i-1]:.1%}")
    print("Greedy picks (in order, by id):", [n for n in chosen])

    ks = list(range(0, K + 1))
    plt.figure(figsize=(7, 4.2))
    for name, cv, st in (("Greedy planner", g_curve, "-o"), ("Biggest customer cone", c_curve, "--s"),
                         ("Highest degree", d_curve, ":^"), ("Random (avg of 5)", r_curve, "-.x")):
        plt.plot(ks, [none] + cv, st, label=name)
    plt.xlabel("Indian networks enabling ROV (k)")
    plt.ylabel("Avg share of networks hijacked")
    plt.title("Toy model: which networks should check routes first?\n(synthetic data, concept demo)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("toy_results.png", dpi=150)
    print("\nSaved toy_results.png")
