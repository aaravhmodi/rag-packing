"""
Standalone: generate only the p50/p95/p99 percentile plots, across datasets and/or budgets.
Skips all the other figures in plot.py -- useful once you just want to refresh tail-behavior
plots after adding a new dataset or budget run.

Usage:
  # single dataset/budget
  python percentiles.py --dataset hotpotqa --budget 160

  # every dataset x budget combo found in results/, plus the vs-budget sweep per dataset
  python percentiles.py --all
"""
import argparse
from pathlib import Path

import pandas as pd

import plot as plot_mod


def _discover_runs():
    """Return {dataset: [budgets]} for every results_{dataset}_budget{B}.csv on disk."""
    runs = {}
    for csv in sorted(Path("results").glob("results_*_budget*.csv")):
        stem = csv.stem  # results_{dataset}_budget{B}
        rest = stem[len("results_"):]
        dataset, _, budget_str = rest.rpartition("_budget")
        runs.setdefault(dataset, []).append(int(budget_str))
    return runs


def run_one(dataset: str, budget: int):
    csv = Path("results") / f"results_{dataset}_budget{budget}.csv"
    if not csv.exists():
        raise FileNotFoundError(f"Expected {csv} -- run evaluate.py first.")
    df = pd.read_csv(csv)
    out = Path("plots")
    out.mkdir(exist_ok=True)
    plot_mod.plot_percentiles(df, out, f"{dataset}_budget{budget}")


def run_all():
    runs = _discover_runs()
    if not runs:
        raise FileNotFoundError("No results_*_budget*.csv files found in results/. Run evaluate.py or sweep.py first.")
    for dataset, budgets in runs.items():
        for budget in budgets:
            print(f"\n=== {dataset} @ budget {budget} ===")
            run_one(dataset, budget)
        if len(budgets) > 1:
            print(f"\n=== {dataset} percentiles vs budget ===")
            summary = plot_mod._load_all_budgets(dataset)
            plot_mod.plot_percentiles_vs_budget(summary, Path("plots"), dataset)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default=None)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--all", action="store_true", help="Run for every dataset/budget combo found in results/.")
    args = parser.parse_args()

    if args.all:
        run_all()
    elif args.dataset and args.budget:
        run_one(args.dataset, args.budget)
    else:
        parser.error("Either pass --dataset and --budget, or use --all.")
