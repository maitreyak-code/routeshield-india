"""Join CAIDA topology with the APNIC India list."""
from pathlib import Path
from load_topology import load
from download_apnic import indian_asns

caida = sorted(Path("data").glob("*.as-rel2.txt.bz2"))[-1]
prov, cust, peer = load(caida)
india = indian_asns(Path("data") / "delegated-apnic-latest.txt")

ases = set(prov) | set(cust) | set(peer)
in_map = sorted(a for a in india if a in ases)
transit = [a for a in in_map if len(cust[a]) > 0]
stubs = [a for a in in_map if len(cust[a]) == 0]
single = [a for a in stubs if len(prov[a]) == 1]

print(f"Indian AS numbers assigned: {len(india)}")
print(f"...of those, present in the map: {len(in_map)}")
print(f"Indian networks with customers (transit): {len(transit)}")
print(f"Indian stub networks (no customers): {len(stubs)}")
print(f"...with a single upstream: {len(single)}")
print("AS18101 upstream(s):", sorted(prov[18101]))
top = sorted(transit, key=lambda a: -len(cust[a]))[:8]
print("Top 8 Indian networks by customers:", [(a, len(cust[a])) for a in top])