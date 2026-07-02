"""
Prepare a local HotpotQA export for offline evaluation.

Examples:
  python prepare_hotpotqa.py --split validation --output data/hotpot_qa_validation.jsonl
  python prepare_hotpotqa.py --split validation --output data/hotpot_qa_validation --format disk

This script still needs network access the first time it downloads HotpotQA.
Once exported, evaluate.py can run offline with --data_file.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from datasets import load_dataset


def main(split: str, output: str, fmt: str):
    ds = load_dataset("hotpot_qa", "distractor", split=split)
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "disk":
        ds.save_to_disk(str(out))
        print(f"Saved dataset directory -> {out}")
        return

    if fmt == "jsonl":
        ds.to_json(str(out), orient="records", lines=True)
    elif fmt == "json":
        ds.to_json(str(out), orient="records")
    elif fmt == "csv":
        ds.to_csv(str(out))
    elif fmt == "parquet":
        ds.to_parquet(str(out))
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    print(f"Saved {fmt} export -> {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", type=str, default="validation")
    parser.add_argument("--output", type=str, default="data/hotpot_qa_validation.jsonl")
    parser.add_argument("--format", type=str, default="jsonl", choices=["jsonl", "json", "csv", "parquet", "disk"])
    args = parser.parse_args()
    main(args.split, args.output, args.format)
