"""
Main evaluation loop.

Usage:
  python evaluate.py --budget 160 --n_questions 200 --split validation
"""
import argparse
import json
import random
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from tqdm import tqdm

from retrieve import chunk_supporting_facts, retrieve
from pack import pack_topk, pack_mmr, pack_focused, pack_answer_survival
from reader import generate_answer
from metrics import token_f1, exact_match, answer_in_context, avg_token_cost

METHODS = {
    "topk":            pack_topk,
    "mmr":             pack_mmr,
    "focused":         pack_focused,
    "answer_survival": pack_answer_survival,
}


def run(budget: int, n_questions: int, split: str, seed: int = 42):
    random.seed(seed)
    ds = load_dataset("hotpot_qa", "distractor", split=split, trust_remote_code=True)
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
            row[f"{name}_aic"]   = int(answer_in_context(gold, packed))
            row[f"{name}_f1"]    = token_f1(pred, gold)
            row[f"{name}_em"]    = exact_match(pred, gold)
            row[f"{name}_tokens"] = sum(len(c["text"].split()) for c in packed)
        records.append(row)

    df = pd.DataFrame(records)
    out = Path("results") / f"results_budget{budget}.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved → {out}")
    _print_summary(df, budget)
    return df


def _print_summary(df, budget):
    print(f"\n=== Budget {budget} tokens ===")
    header = f"{'Method':<18} {'AIC':>6} {'F1':>6} {'EM':>6} {'Tokens':>8}"
    print(header)
    print("-" * len(header))
    for name in METHODS:
        aic    = df[f"{name}_aic"].mean()
        f1     = df[f"{name}_f1"].mean()
        em     = df[f"{name}_em"].mean()
        tokens = df[f"{name}_tokens"].mean()
        print(f"{name:<18} {aic:>6.3f} {f1:>6.3f} {em:>6.3f} {tokens:>8.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget",      type=int, default=160)
    parser.add_argument("--n_questions", type=int, default=200)
    parser.add_argument("--split",       type=str, default="validation")
    args = parser.parse_args()
    run(args.budget, args.n_questions, args.split)
