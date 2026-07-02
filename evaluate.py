"""
Main evaluation loop.

Usage:
  python evaluate.py --budget 160 --n_questions 200 --split validation
  python evaluate.py --budget 160 --n_questions 200 --data_file data/hotpot_qa_validation.jsonl
"""
import argparse
import os
import random
from pathlib import Path

import pandas as pd
from datasets import Dataset, DatasetDict, load_dataset, load_from_disk
from tqdm import tqdm

from retrieve import chunk_supporting_facts, retrieve
from pack import pack_topk, pack_mmr, pack_focused, pack_answer_survival
from reader import generate_answer
from metrics import token_f1, exact_match, answer_in_context

METHODS = {
    "topk": pack_topk,
    "mmr": pack_mmr,
    "focused": pack_focused,
    "answer_survival": pack_answer_survival,
}


def _hf_token() -> str | None:
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
    if token:
        return token

    env_path = Path(".env")
    if not env_path.exists():
        return None

    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in {"HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"}:
            return value.strip().strip("'\"")
    return None


def _load_dataset(split: str, data_file: str | None):
    if data_file:
        path = Path(data_file)
        if not path.exists():
            raise FileNotFoundError(f"Local dataset file not found: {path}")

        suffix = path.suffix.lower()
        if path.is_dir():
            loaded = load_from_disk(str(path))
            if isinstance(loaded, DatasetDict):
                if split not in loaded:
                    raise KeyError(f"Split '{split}' not found in saved dataset directory: {path}")
                return loaded[split]
            return loaded
        if suffix in {".json", ".jsonl"}:
            return Dataset.from_json(str(path))
        if suffix == ".csv":
            return Dataset.from_csv(str(path))
        if suffix == ".parquet":
            return Dataset.from_parquet(str(path))
        raise ValueError(
            "Unsupported local dataset format. Use a saved dataset directory or one of: "
            ".json, .jsonl, .csv, .parquet."
        )

    try:
        return load_dataset("hotpot_qa", "distractor", split=split, token=_hf_token())
    except Exception as exc:
        cache_root = Path.home() / ".cache" / "huggingface" / "hub" / "datasets--hotpot_qa"
        raise RuntimeError(
            "Failed to load HotpotQA. Provide a local dataset with --data_file or restore "
            f"the Hugging Face cache at {cache_root}."
        ) from exc


def run(budget: int, n_questions: int, split: str, data_file: str | None = None, seed: int = 42):
    random.seed(seed)
    ds = _load_dataset(split, data_file)
    indices = random.sample(range(len(ds)), min(n_questions, len(ds)))

    records = []
    for idx in tqdm(indices, desc="questions"):
        ex = ds[idx]
        question = ex["question"]
        gold = ex["answer"]
        chunks = chunk_supporting_facts(ex)
        candidates = retrieve(question, chunks, top_n=20)

        row = {"question": question, "gold": gold}
        for name, packer in METHODS.items():
            packed = packer(question, candidates, budget)
            pred = generate_answer(question, packed)
            row[f"{name}_aic"] = int(answer_in_context(gold, packed))
            row[f"{name}_f1"] = token_f1(pred, gold)
            row[f"{name}_em"] = exact_match(pred, gold)
            row[f"{name}_tokens"] = sum(len(c["text"].split()) for c in packed)
        records.append(row)

    df = pd.DataFrame(records)
    out = Path("results") / f"results_budget{budget}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nSaved -> {out}")
    _print_summary(df, budget)
    return df


def _print_summary(df, budget):
    print(f"\n=== Budget {budget} tokens ===")
    header = f"{'Method':<18} {'AIC':>6} {'F1':>6} {'EM':>6} {'Tokens':>8}"
    print(header)
    print("-" * len(header))
    for name in METHODS:
        aic = df[f"{name}_aic"].mean()
        f1 = df[f"{name}_f1"].mean()
        em = df[f"{name}_em"].mean()
        tokens = df[f"{name}_tokens"].mean()
        print(f"{name:<18} {aic:>6.3f} {f1:>6.3f} {em:>6.3f} {tokens:>8.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=160)
    parser.add_argument("--n_questions", type=int, default=200)
    parser.add_argument("--split", type=str, default="validation")
    parser.add_argument(
        "--data_file",
        type=str,
        default=None,
        help="Optional local HotpotQA export (.json, .jsonl, .csv, .parquet, or a saved dataset directory).",
    )
    args = parser.parse_args()
    run(args.budget, args.n_questions, args.split, args.data_file)
