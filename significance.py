"""
Paired bootstrap significance testing between AnswerSurvival and each baseline.

Since all methods are evaluated on the same questions, differences are paired --
we bootstrap-resample questions (not method scores independently) to get a
distribution of the paired difference in means, then report a 95% CI and a
two-sided p-value (fraction of bootstrap draws where the sign flips).

Usage:
  python significance.py --dataset hotpotqa --budget 160
  python significance.py --dataset hotpotqa --budget 160 --n_boot 10000
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

METHODS = ["topk", "mmr", "focused"]
TREATMENT = "answer_survival"


def paired_bootstrap(a: np.ndarray, b: np.ndarray, n_boot: int, seed: int = 0):
    """Return (mean_diff, ci_low, ci_high, p_value) for mean(a) - mean(b), paired by index."""
    rng = np.random.default_rng(seed)
    n = len(a)
    diffs = a - b
    observed = diffs.mean()

    boot_means = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        boot_means[i] = diffs[idx].mean()

    ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])
    # two-sided p-value: fraction of bootstrap draws on the other side of 0 from the observed effect
    if observed >= 0:
        p = 2 * min((boot_means <= 0).mean(), 0.5)
    else:
        p = 2 * min((boot_means >= 0).mean(), 0.5)
    p = min(p, 1.0)
    return observed, ci_low, ci_high, p


def run(dataset: str, budget: int, n_boot: int, metrics: list[str]):
    csv = Path("results") / f"results_{dataset}_budget{budget}.csv"
    if not csv.exists():
        raise FileNotFoundError(f"Run evaluate.py first. Expected: {csv}")
    df = pd.read_csv(csv)

    rows = []
    for metric in metrics:
        treat = df[f"{TREATMENT}_{metric}"].to_numpy()
        for baseline in METHODS:
            base = df[f"{baseline}_{metric}"].to_numpy()
            diff, lo, hi, p = paired_bootstrap(treat, base, n_boot)
            rows.append({
                "metric": metric,
                "baseline": baseline,
                "mean_diff": diff,
                "ci_low": lo,
                "ci_high": hi,
                "p_value": p,
                "significant_95": bool(lo > 0 or hi < 0),
            })

    result = pd.DataFrame(rows)
    out = Path("results") / f"significance_{dataset}_budget{budget}.csv"
    result.to_csv(out, index=False)

    print(f"\n=== AnswerSurvival vs baselines ({dataset}, budget={budget}, n={len(df)}, {n_boot} bootstrap draws) ===")
    header = f"{'Metric':<8} {'Baseline':<16} {'Diff':>8} {'95% CI':>20} {'p':>8} {'Sig?':>6}"
    print(header)
    print("-" * len(header))
    for _, r in result.iterrows():
        ci = f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}]"
        sig = "yes" if r["significant_95"] else "no"
        print(f"{r['metric']:<8} {r['baseline']:<16} {r['mean_diff']:>+8.3f} {ci:>20} {r['p_value']:>8.4f} {sig:>6}")
    print(f"\nSaved -> {out}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="hotpotqa")
    parser.add_argument("--budget", type=int, default=160)
    parser.add_argument("--n_boot", type=int, default=5000)
    parser.add_argument("--metrics", type=str, nargs="+", default=["aic", "f1", "em"])
    args = parser.parse_args()
    run(args.dataset, args.budget, args.n_boot, args.metrics)
