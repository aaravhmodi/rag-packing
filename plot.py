"""
Generate the 5 paper figures from results CSVs.

Usage:
  python plot.py --budget 160
"""
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

METHODS   = ["topk", "mmr", "focused", "answer_survival"]
LABELS    = ["Top-K", "MMR", "Focused", "AnswerSurvival"]
PALETTE   = ["#6baed6", "#fd8d3c", "#74c476", "#e377c2"]

sns.set_theme(style="whitegrid", font_scale=1.15)


def bar(ax, values, title, ylabel):
    bars = ax.bar(LABELS, values, color=PALETTE, width=0.55, edgecolor="white")
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(values) * 1.25)
    for bar_, v in zip(bars, values):
        ax.text(bar_.get_x() + bar_.get_width() / 2, bar_.get_height() + 0.005,
                f"{v:.3f}", ha="center", va="bottom", fontsize=10)


def plot_failure_modes(df, out_dir):
    """Stacked bar of failure categories for each method."""
    cats = {
        "AIC but low F1":        lambda d, m: ((d[f"{m}_aic"] == 1) & (d[f"{m}_f1"] < 0.3)).mean(),
        "Not in context":        lambda d, m: (d[f"{m}_aic"] == 0).mean(),
        "Context ok, reader fail": lambda d, m: ((d[f"{m}_aic"] == 1) & (d[f"{m}_f1"] >= 0.3)).mean(),
    }
    data = {label: [fn(df, m) for m in METHODS] for label, fn in cats.items()}

    fig, ax = plt.subplots(figsize=(8, 5))
    bottom = [0.0] * len(METHODS)
    colors = ["#fc8d59", "#d73027", "#91bfdb"]
    for (cat, vals), color in zip(data.items(), colors):
        ax.bar(LABELS, vals, bottom=bottom, label=cat, color=color, edgecolor="white")
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_title("Failure Mode Breakdown", fontweight="bold")
    ax.set_ylabel("Fraction of questions")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_dir / "fig5_failure_modes.png", dpi=150)
    plt.close()
    print("  saved fig5_failure_modes.png")


def main(budget):
    csv = Path("results") / f"results_budget{budget}.csv"
    if not csv.exists():
        raise FileNotFoundError(f"Run evaluate.py first. Expected: {csv}")
    df = pd.read_csv(csv)
    out = Path("plots")
    out.mkdir(exist_ok=True)

    metrics = [
        ("aic",    "Answer-in-Context Rate",   "Rate",       "fig1_aic.png"),
        ("f1",     "F1 Score",                 "F1",         "fig2_f1.png"),
        ("em",     "Exact Match",              "EM",         "fig3_em.png"),
        ("tokens", "Avg Token Cost",           "Tokens",     "fig4_tokens.png"),
    ]

    for col, title, ylabel, fname in metrics:
        vals = [df[f"{m}_{col}"].mean() for m in METHODS]
        fig, ax = plt.subplots(figsize=(7, 4))
        bar(ax, vals, f"{title} (budget={budget})", ylabel)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=150)
        plt.close()
        print(f"  saved {fname}")

    plot_failure_modes(df, out)
    print(f"\nAll plots written to {out}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=160)
    args = parser.parse_args()
    main(args.budget)
