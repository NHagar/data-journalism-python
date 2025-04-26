"""fetch_datasets.py
Download tutorial datasets for The Art of Data Journalism Jupyter Book.

Uses lowercase *state names* (with hyphens for multi-word states) instead of postal abbreviations.

Usage:
    python fetch_datasets.py                        # downloads into ./_static
    python fetch_datasets.py --dest path/to/dir     # custom destination
    python fetch_datasets.py --states new-york,texas
"""

import argparse
import concurrent.futures
from pathlib import Path

import requests

STATE_NAMES = [
    "alabama",
    "alaska",
    "arizona",
    "arkansas",
    "california",
    "colorado",
    "connecticut",
    "delaware",
    "florida",
    "georgia",
    "hawaii",
    "idaho",
    "illinois",
    "indiana",
    "iowa",
    "kansas",
    "kentucky",
    "louisiana",
    "maine",
    "maryland",
    "massachusetts",
    "michigan",
    "minnesota",
    "mississippi",
    "missouri",
    "montana",
    "nebraska",
    "nevada",
    "new-hampshire",
    "new-jersey",
    "new-mexico",
    "new-york",
    "north-carolina",
    "north-dakota",
    "ohio",
    "oklahoma",
    "oregon",
    "pennsylvania",
    "rhode-island",
    "south-carolina",
    "south-dakota",
    "tennessee",
    "texas",
    "utah",
    "vermont",
    "virginia",
    "washington",
    "west-virginia",
    "wisconsin",
    "wyoming",
]

PATTERNED_URLS = [
    "https://the-art-of-data-journalism.github.io/tutorial-data/census-estimates/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/nursing-homes/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/rural-grants/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/plane-crashes/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/government-census/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/unemployment-rates/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/colleges/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/uninsured/{state}.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/fatal-accidents/{state}-accidents.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/fatal-accidents/{state}-people.csv",
]

SINGLE_URLS = [
    "https://the-art-of-data-journalism.github.io/tutorial-data/plane-crashes-cleaning/crashes-for-cleaning.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/greenhouse-gas-emitters/ghgp_data_2022.xlsx",
    "https://the-art-of-data-journalism.github.io/tutorial-data/state-legislatures/legislatures.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/unemployment-rates/national.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/peak-unemployment/peak.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/college-cost/national.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/college-cost/bigpublic.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/college-cost/accredited.csv",
    "https://the-art-of-data-journalism.github.io/tutorial-data/groundhogs/predictions2024.csv",
]


def iter_urls(states):
    for tmpl in PATTERNED_URLS:
        for st in states:
            yield tmpl.format(state=st)
    for url in SINGLE_URLS:
        yield url


def mirror_path(url, dest_root):
    rel = url.split("/tutorial-data/")[-1]
    return Path(dest_root, rel)


def fetch(url, dest_root, timeout=30):
    dest = mirror_path(url, dest_root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return url, "exists"
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return url, f"ok {len(r.content):,} bytes"
    except Exception as e:
        return url, f"ERROR: {e}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dest", default="_static")
    p.add_argument("--states", help="comma‑separated list of state names")
    p.add_argument("--workers", type=int, default=8)
    args = p.parse_args()

    states = (
        STATE_NAMES
        if not args.states
        else [s.strip().lower() for s in args.states.split(",")]
    )

    urls = list(iter_urls(states))
    dest_root = Path(args.dest)
    dest_root.mkdir(exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for u, status in ex.map(lambda u: fetch(u, dest_root), urls):
            print(f"{u} -> {status}")


if __name__ == "__main__":
    main()
