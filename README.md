# \# RouteShield India

# 

# \*\*Question:\*\* Which Indian networks should start checking route announcements first, to stop fake announcements from spreading?

# 

# \## Status

#Early work in progress. Real-data replay of the June 2026 incident works; the planner on real data is not built yet. toy_sim.py is a synthetic concept demo.

# 

# \## Related work

# The method is not new. This project builds on earlier work on prioritising ROV deployment, including Chen et al., "More Bang for Your Buck", and Gilad et al., NDSS 2017.

# 

# \## Safety

# Only passive public data and simulation. No route announcements, no probing of real networks.
## Results so far: replay of the 16 June 2026 incident
Attacker AS18101 (Rcom), victim AS62041 (Telegram), real CAIDA topology
(1 Nov 2026), simplified Gao-Rexford routing. Share of networks that end up
routing to the attacker:

| Who checks (ROV) | Hijack reaches |
|---|---|
| Nobody | 39.8% |
| AS15412 (FLAG) only | 2.2% |
| AS9498 + AS4755 only | 37.7% |
| AS15412 + AS9498 + AS4755 | 0.0% |

FLAG is Rcom's only upstream, so it does most of the work; the other two
close the remainder. This agrees in direction with Kentik's analysis.
If the biggest networks already filter, the benefit of adding FLAG shrinks
(see `incident_sensitivity.py`).

## Limitations
- Absolute numbers are not comparable to Kentik's 1.6% (different
  denominator, and our baseline assumes little existing ROV).
- CAIDA relationships are inferred; one prefix, simplified routing rules.
- Per-network ROV status is uncertain (APNIC and RoVista disagree);
  see DATA_NOTES.md. Results are shown under assumptions, not as facts.

## Data and credit
- CAIDA AS Relationships Dataset, 20261101 (downloaded by script, not committed).
- APNIC delegated statistics (India AS list); APNIC Labs RPKI measurements.
- Related work: Chen et al., "More Bang for Your Buck"; Gilad et al.,
  NDSS 2017; Kentik and Anurag Bhatia on the June 2026 incident.

## Reproduce
pip install -r requirements.txt
python download_caida.py
python download_apnic.py
python bgpsim.py
