"""Download the newest CAIDA AS-relationships file (serial-2) into ./data."""
import re
import urllib.request
from pathlib import Path

BASE = "https://data.caida.org/datasets/as-relationships/serial-2/"
OUT = Path("data")


def main():
    OUT.mkdir(exist_ok=True)
    html = urllib.request.urlopen(BASE, timeout=60).read().decode()
    files = sorted(set(re.findall(r'\d{8}\.as-rel2\.txt\.bz2', html)))
    if not files:
        raise SystemExit("No as-rel2 files found on the CAIDA page.")
    latest = files[-1]
    dest = OUT / latest
    if dest.exists():
        print(f"Already have {latest}")
        return
    print(f"Downloading {latest} ...")
    urllib.request.urlretrieve(BASE + latest, dest)
    print(f"Saved {dest} ({dest.stat().st_size // 1024} KB)")
    print('Cite as: The CAIDA AS Relationships Dataset, ' + latest[:8])


if __name__ == "__main__":
    main()