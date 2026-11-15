"""Validate the configured stock YAML and generate CSV and SQLite outputs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from stock_analysis.pipeline import process_source


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="YAML source file (defaults to STOCK_DATA_PATH or data/raw/)")
    parser.add_argument("--sectors", help="Optional sector CSV (defaults to data/raw/sectors.csv)")
    parser.add_argument("--output", help="Output directory (defaults to data/processed)")
    args = parser.parse_args()
    kwargs = {}
    if args.output:
        kwargs["output_dir"] = args.output
    _, _, report = process_source(args.source, args.sectors, **kwargs)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
