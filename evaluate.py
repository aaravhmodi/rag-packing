"""
Main evaluation loop.

Usage:
  python evaluate.py --dataset hotpotqa --budget 160 --n_questions 200 --split validation
  python evaluate.py --dataset squad --budget 160 --n_questions 200 --split validation
  python evaluate.py --dataset hotpotqa --budget 160 --n_questions 200 --data_file data/hotpot_qa_validation.jsonl
"""
import argparse
import random
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from datasets_adapter import load_examples
from retrieve import retrieve
from pack import pack_topk, pack_mmr, pack_focused, pack_answer_survival
from reader import generate_answer
from metrics import token_f1, exact_match, answer_in_context

METHODS = {
    "topk": pack_topk,
    "mmr": pack_mmr,
    "focused": pack_focused,
    "answer_survival": pack_answer_survival,
}


def run(dataset: str, budget: int, n_questions: int, split: str, data_file: str | None = None, seed: int = 42):
    random.seed(seed)
    examples = load_examples(dataset, split, data_file)
    if not examples:
        raise RuntimeError(f"No usable examples loaded for dataset '{dataset}' split '{split}'.")
    picked = random.sample(examples, min(n_questions, len(examples)))

    records = []
    for ex in tqdm(picked, desc="questions"):
        question = ex["question"]
        gold = ex["answer"]
        candidates = retrieve(question, ex["chunks"], top_n=20)

        row = {"question": question, "gold": gold, "qtype": ex.get("qtype")}
        for name, packer in METHODS.items():
            packed = packer(question, candidates, budget)
            pred = generate_answer(question, packed)
            row[f"{name}_aic"] = int(answer_in_context(gold, packed))
            row[f"{name}_f1"] = token_f1(pred, gold)
            row[f"{name}_em"] = exact_match(pred, gold)
            row[f"{name}_tokens"] = sum(len(c["text"].split()) for c in packed)
        records.append(row)

    df = pd.DataFrame(records)
    out = Path("results") / f"results_{dataset}_budget{budget}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nSaved -> {out}")
    _print_summary(df, dataset, budget)
    return df


def _print_summary(df, dataset, budget):
    print(f"\n=== {dataset} | Budget {budget} tokens ===")
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
    parser.add_argument("--dataset", type=str, default="hotpotqa",
                         choices=["hotpotqa", "squad", "triviaqa", "2wikimultihopqa"])
    parser.add_argument("--budget", type=int, default=160)
    parser.add_argument("--n_questions", type=int, default=200)
    parser.add_argument("--split", type=str, default="validation")
    parser.add_argument(
        "--data_file",
        type=str,
        default=None,
        help="Optional local export (.json, .jsonl, .csv, .parquet, or a saved dataset directory). "
             "May be in the dataset's native schema or the unified question/answer/qtype/chunks schema.",
    )
    args = parser.parse_args()
    run(args.dataset, args.budget, args.n_questions, args.split, args.data_file)
