\# Data notes (checked 11 Nov 2026)



\## ROV status source: APNIC Labs (stats.labs.apnic.net/rpki/IN)

\- Per-network "RPKI Validates" % and sample counts are published for India.

\- Measures end users, so pure transit networks (e.g. AS15412) do not appear.

\- A network's score can come from its upstream, not only itself.

\- Small networks have very few samples; use a minimum-sample cutoff.

\- The country-level series is jumpy (e.g. \~50% in 2023, then \~0).



\## Key networks seen (RPKI Validates, samples)

\- AS9498 Airtel: 3.42% (937)

\- AS4755 Tata: 19.24% (343)

\- AS18101 Rcom: 0% (16, too few to trust)

\- AS15412 FLAG: not listed



\## Still unverified

\- Second source for transit networks (e.g. RoVista)

\- CAIDA AS-relationship data terms of use

\## Second source: RoVista (rovista.netsecurelab.org), checked 11 Nov 2026

\- Scores (9 Oct 2026): AS15412 100%, AS9498 100%, AS4755 0%, AS18101 0%.

\- Conflicts with APNIC for Airtel (100% vs 3.4%): methods differ

&#x20; (RoVista = reachability of invalid prefixes; APNIC = users protected).

\- AS9498 and AS15412 history charts are near-identical: 0 until early

&#x20; Feb 2026, then 100. Only \~3 invalid prefixes tested by then, so weak evidence.

&#x20; No change visible around 16 Jun 2026.

\- Conclusion: per-network ROV status is uncertain. Treat it as an

&#x20; assumption and test sensitivity; do not claim to confirm Kentik.

\## Topology source: CAIDA AS Relationships (checked 11 Nov 2026)

\- Public download: data.caida.org/datasets/as-relationships/serial-2/

\- Format: provider|customer|-1 and peer|peer|0.

\- Terms: CAIDA Acceptable Use Agreement. Cite as "The CAIDA AS

&#x20; Relationships Dataset, <date range used>" and notify CAIDA of publications.

\- Plan: download via script, do not commit the data files. Read the full

&#x20; AUA before publishing results.

