"""
Run evaluate.py across multiple datasets x token budgets, then generate all plots.

Usage:
  python sweep.py --n_questions 200
  python sweep.py --n_questions 200 --datasets hotpotqa squad --budgets 160 256
"""
import argparse
import subprocess
import sys

import plot as plot_mod

DEFAULT_DATASETS = ["hotpotqa", "squad", "2wikimultihopqa", "triviaqa"]
DEFAULT_BUDGETS = [80, 160, 256, 384, 512]


def main(datasets, budgets, n_questions, split):
    for dataset in datasets:
        for budget in budgets:
            cmd = [sys.executable, "evaluate.py", "--dataset", dataset, "--budget", str(budget),
                   "--n_questions", str(n_questions), "--split", split]
            print(f"\n=== Running evaluate.py --dataset {dataset} --budget {budget} ===")
            subprocess.run(cmd, check=True)
            plot_mod.single_budget(dataset, budget)

        if len(budgets) > 1:
            print(f"\n=== Multi-budget plots for {dataset} ===")
            plot_mod.sweep_plots(dataset)

    if len(datasets) > 1:
        for budget in budgets:
            print(f"\n=== Cross-dataset plot for budget {budget} ===")
            try:
                plot_mod.cross_dataset_plot(budget)
            except FileNotFoundError as exc:
                print(f"  skipped: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", type=str, nargs="+", default=DEFAULT_DATASETS)
    parser.add_argument("--budgets", type=int, nargs="+", default=DEFAULT_BUDGETS)
    parser.add_argument("--n_questions", type=int, default=200)
    parser.add_argument("--split", type=str, default="validation")
    args = parser.parse_args()
    main(args.datasets, args.budgets, args.n_questions, args.split)
