"""Download APNIC's delegation file and list Indian (IN) AS numbers."""
import urllib.request
from pathlib import Path

URL = "https://ftp.apnic.net/stats/apnic/delegated-apnic-latest"
OUT = Path("data")


def indian_asns(path):
    asns = set()
    for line in open(path, encoding="utf-8"):
        p = line.strip().split("|")
        if len(p) >= 7 and p[1] == "IN" and p[2] == "asn":
            start, count = int(p[3]), int(p[4])
            asns.update(range(start, start + count))
    return asns


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    dest = OUT / "delegated-apnic-latest.txt"
    urllib.request.urlretrieve(URL, dest)
    asns = indian_asns(dest)
    print(f"Indian AS numbers: {len(asns)}")
    for a in (18101, 15412, 9498, 4755):
        print(f"AS{a} in India list: {a in asns}")