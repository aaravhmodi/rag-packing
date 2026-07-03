"""
Run evaluate.py across multiple token budgets, then generate all plots.

Usage:
  python sweep.py --n_questions 200
  python sweep.py --n_questions 200 --budgets 80 160 256 512
"""
import argparse
import subprocess
import sys

import plot as plot_mod

DEFAULT_BUDGETS = [80, 160, 256, 384, 512]


def main(budgets, n_questions, split, data_file):
    for budget in budgets:
        cmd = [sys.executable, "evaluate.py", "--budget", str(budget),
               "--n_questions", str(n_questions), "--split", split]
        if data_file:
            cmd += ["--data_file", data_file]
        print(f"\n=== Running evaluate.py --budget {budget} ===")
        subprocess.run(cmd, check=True)
        plot_mod.single_budget(budget)

    print("\n=== Generating multi-budget comparison plots ===")
    plot_mod.sweep_plots()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--budgets", type=int, nargs="+", default=DEFAULT_BUDGETS)
    parser.add_argument("--n_questions", type=int, default=200)
    parser.add_argument("--split", type=str, default="validation")
    parser.add_argument("--data_file", type=str, default=None)
    args = parser.parse_args()
    main(args.budgets, args.n_questions, args.split, args.data_file)
