"""
Generate qualitative examples (question, gold answer, per-method packed context +
prediction) as a markdown table for the paper appendix.

Usage:
  python qualitative.py --dataset hotpotqa --budget 160 --n_examples 5
"""
import argparse
import random
from pathlib import Path

from datasets_adapter import load_examples
from retrieve import retrieve
from pack import pack_topk, pack_mmr, pack_focused, pack_answer_survival
from reader import generate_answer, build_context
from metrics import token_f1, exact_match, answer_in_context

METHODS = {
    "topk": pack_topk,
    "mmr": pack_mmr,
    "focused": pack_focused,
    "answer_survival": pack_answer_survival,
}
LABELS = {"topk": "Top-K", "mmr": "MMR", "focused": "Focused", "answer_survival": "AnswerSurvival"}


def _truncate(text: str, n: int = 220) -> str:
    return text if len(text) <= n else text[:n].rstrip() + "..."


def run(dataset: str, budget: int, n_examples: int, split: str, seed: int, mode: str):
    random.seed(seed)
    examples = load_examples(dataset, split)
    picked = random.sample(examples, min(n_examples * 20, len(examples)))

    chosen = []
    for ex in picked:
        question, gold = ex["question"], ex["answer"]
        candidates = retrieve(question, ex["chunks"], top_n=20)
        per_method = {}
        for name, packer in METHODS.items():
            packed = packer(question, candidates, budget)
            pred = generate_answer(question, packed)
            per_method[name] = {
                "context": build_context(packed),
                "pred": pred,
                "aic": answer_in_context(gold, packed),
                "f1": token_f1(pred, gold),
                "em": exact_match(pred, gold),
            }

        as_f1 = per_method["answer_survival"]["f1"]
        base_f1 = max(per_method[m]["f1"] for m in ("topk", "mmr", "focused"))
        if mode == "wins" and as_f1 <= base_f1:
            continue
        if mode == "losses" and as_f1 >= base_f1:
            continue

        chosen.append((question, gold, per_method))
        if len(chosen) >= n_examples:
            break

    if not chosen:
        raise RuntimeError(f"No examples matched mode='{mode}'. Try a different --mode or more --n_examples candidates.")

    lines = [f"# Qualitative Examples -- {dataset} (budget={budget}, mode={mode})\n"]
    for i, (question, gold, per_method) in enumerate(chosen, 1):
        lines.append(f"## Example {i}\n")
        lines.append(f"**Question:** {question}\n")
        lines.append(f"**Gold answer:** {gold}\n")
        lines.append("| Method | Prediction | AIC | F1 | EM | Packed context (truncated) |")
        lines.append("|---|---|---|---|---|---|")
        for name in METHODS:
            r = per_method[name]
            lines.append(
                f"| {LABELS[name]} | {r['pred']} | {int(r['aic'])} | {r['f1']:.2f} | "
                f"{int(r['em'])} | {_truncate(r['context'])} |"
            )
        lines.append("")

    out_dir = Path("plots")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"qualitative_{dataset}_budget{budget}_{mode}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {len(chosen)} examples -> {out}")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="hotpotqa")
    parser.add_argument("--budget", type=int, default=160)
    parser.add_argument("--n_examples", type=int, default=5)
    parser.add_argument("--split", type=str, default="validation")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mode", type=str, default="wins", choices=["wins", "losses", "any"],
                         help="wins: AnswerSurvival beats all baselines on F1. "
                              "losses: AnswerSurvival underperforms. any: no filtering.")
    args = parser.parse_args()
    run(args.dataset, args.budget, args.n_examples, args.split, args.seed, args.mode)
