"""
Generate paper-ready plots from results CSVs.

Single dataset/budget figures:
  python plot.py --dataset hotpotqa --budget 160

Multi-budget comparison for one dataset (needs multiple budgets run):
  python plot.py --dataset hotpotqa --sweep

Cross-dataset comparison at a fixed budget (needs multiple datasets run):
  python plot.py --budget 160 --cross_dataset
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

METHODS = ["topk", "mmr", "focused", "answer_survival"]
LABELS = ["Top-K", "MMR", "Focused", "AnswerSurvival"]
PALETTE = ["#6baed6", "#fd8d3c", "#74c476", "#e377c2"]

sns.set_theme(style="whitegrid", font_scale=1.15)


def _ci95(values):
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n < 2:
        return 0.0
    return 1.96 * values.std(ddof=1) / np.sqrt(n)


def _results_path(dataset, budget):
    return Path("results") / f"results_{dataset}_budget{budget}.csv"


def bar_with_ci(ax, df, col, title, ylabel):
    means = [df[f"{m}_{col}"].mean() for m in METHODS]
    cis = [_ci95(df[f"{m}_{col}"]) for m in METHODS]
    bars = ax.bar(LABELS, means, yerr=cis, capsize=5, color=PALETTE,
                   width=0.55, edgecolor="white")
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(means) * 1.3 if max(means) > 0 else 1)
    for bar_, v in zip(bars, means):
        ax.text(bar_.get_x() + bar_.get_width() / 2, bar_.get_height() + 0.01,
                 f"{v:.3f}", ha="center", va="bottom", fontsize=10)


def plot_failure_modes(df, out_dir, tag):
    cats = {
        "Not in context": lambda d, m: (d[f"{m}_aic"] == 0).mean(),
        "Context ok, reader fail": lambda d, m: ((d[f"{m}_aic"] == 1) & (d[f"{m}_f1"] < 0.3)).mean(),
        "Correct (AIC & F1 ok)": lambda d, m: ((d[f"{m}_aic"] == 1) & (d[f"{m}_f1"] >= 0.3)).mean(),
    }
    data = {label: [fn(df, m) for m in METHODS] for label, fn in cats.items()}

    fig, ax = plt.subplots(figsize=(8, 5))
    bottom = [0.0] * len(METHODS)
    colors = ["#d73027", "#fc8d59", "#91bfdb"]
    for (cat, vals), color in zip(data.items(), colors):
        ax.bar(LABELS, vals, bottom=bottom, label=cat, color=color, edgecolor="white")
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_title(f"Failure Mode Breakdown ({tag})", fontweight="bold")
    ax.set_ylabel("Fraction of questions")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_dir / f"fig5_failure_modes_{tag}.png", dpi=150)
    plt.close()
    print(f"  saved fig5_failure_modes_{tag}.png")


def plot_aic_vs_f1_scatter(df, out_dir, tag):
    fig, axes = plt.subplots(1, len(METHODS), figsize=(4 * len(METHODS), 4), sharey=True)
    for ax, m, label, color in zip(axes, METHODS, LABELS, PALETTE):
        x = df[f"{m}_aic"] + np.random.uniform(-0.03, 0.03, len(df))
        y = df[f"{m}_f1"]
        ax.scatter(x, y, alpha=0.4, s=18, color=color)
        r = np.corrcoef(df[f"{m}_aic"], df[f"{m}_f1"])[0, 1] if df[f"{m}_aic"].nunique() > 1 else float("nan")
        ax.set_title(f"{label}\nr={r:.2f}", fontsize=11)
        ax.set_xlabel("Answer in Context")
        ax.set_xticks([0, 1])
    axes[0].set_ylabel("Token F1")
    fig.suptitle(f"AIC vs F1 per question ({tag})", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / f"fig6_aic_vs_f1_{tag}.png", dpi=150)
    plt.close()
    print(f"  saved fig6_aic_vs_f1_{tag}.png")


def plot_f1_violin(df, out_dir, tag):
    long_df = pd.melt(
        df, value_vars=[f"{m}_f1" for m in METHODS],
        var_name="method", value_name="f1"
    )
    long_df["method"] = long_df["method"].str.replace("_f1", "", regex=False)
    label_map = dict(zip(METHODS, LABELS))
    long_df["method"] = long_df["method"].map(label_map)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.violinplot(data=long_df, x="method", y="f1", palette=PALETTE, ax=ax, cut=0)
    ax.set_title(f"F1 Score Distribution ({tag})", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Token F1")
    fig.tight_layout()
    fig.savefig(out_dir / f"fig7_f1_dist_{tag}.png", dpi=150)
    plt.close()
    print(f"  saved fig7_f1_dist_{tag}.png")


def plot_aic_gain(df, out_dir, tag):
    baseline = df["topk_aic"].mean()
    gains = [df[f"{m}_aic"].mean() - baseline for m in METHODS]
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#999999" if g == 0 else ("#2ca02c" if g > 0 else "#d62728") for g in gains]
    bars = ax.bar(LABELS, gains, color=colors, edgecolor="white", width=0.55)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"AIC Gain over Top-K Baseline ({tag})", fontweight="bold")
    ax.set_ylabel("Delta AIC rate")
    for bar_, v in zip(bars, gains):
        ax.text(bar_.get_x() + bar_.get_width() / 2,
                 bar_.get_height() + (0.005 if v >= 0 else -0.015),
                 f"{v:+.3f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / f"fig8_aic_gain_{tag}.png", dpi=150)
    plt.close()
    print(f"  saved fig8_aic_gain_{tag}.png")


def plot_by_qtype(df, out_dir, tag):
    """Break down AIC/F1 by question type (e.g. bridge vs comparison), if present."""
    if "qtype" not in df.columns or df["qtype"].dropna().empty:
        return
    types = sorted(df["qtype"].dropna().unique())
    if len(types) < 2:
        return

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    x = np.arange(len(types))
    width = 0.8 / len(METHODS)

    for col, ax, ylabel in zip(["aic", "f1"], axes, ["AIC rate", "F1"]):
        for i, (m, label, color) in enumerate(zip(METHODS, LABELS, PALETTE)):
            vals = [df[df["qtype"] == t][f"{m}_{col}"].mean() for t in types]
            ax.bar(x + i * width, vals, width=width, label=label, color=color, edgecolor="white")
        ax.set_xticks(x + width * (len(METHODS) - 1) / 2)
        ax.set_xticklabels(types)
        ax.set_ylabel(ylabel)
        ax.set_title(f"{ylabel} by question type", fontsize=12)
    axes[0].legend(fontsize=8, loc="upper right")
    fig.suptitle(f"Per-Question-Type Breakdown ({tag})", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / f"fig13_by_qtype_{tag}.png", dpi=150)
    plt.close()
    print(f"  saved fig13_by_qtype_{tag}.png")


def single_budget(dataset, budget):
    csv = _results_path(dataset, budget)
    if not csv.exists():
        raise FileNotFoundError(f"Run evaluate.py first. Expected: {csv}")
    df = pd.read_csv(csv)
    out = Path("plots")
    out.mkdir(exist_ok=True)
    tag = f"{dataset}_budget{budget}"

    metrics = [
        ("aic", "Answer-in-Context Rate", "Rate", f"fig1_aic_{tag}.png"),
        ("f1", "F1 Score", "F1", f"fig2_f1_{tag}.png"),
        ("em", "Exact Match", "EM", f"fig3_em_{tag}.png"),
        ("tokens", "Avg Token Cost", "Tokens", f"fig4_tokens_{tag}.png"),
    ]

    for col, title, ylabel, fname in metrics:
        fig, ax = plt.subplots(figsize=(7, 4))
        bar_with_ci(ax, df, col, f"{title} ({tag})", ylabel)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=150)
        plt.close()
        print(f"  saved {fname}")

    plot_failure_modes(df, out, tag)
    plot_aic_vs_f1_scatter(df, out, tag)
    plot_f1_violin(df, out, tag)
    plot_aic_gain(df, out, tag)
    plot_by_qtype(df, out, tag)
    print(f"\nAll single-run plots written to {out}/")


def _load_all_budgets(dataset):
    results_dir = Path("results")
    rows = []
    for csv in sorted(results_dir.glob(f"results_{dataset}_budget*.csv")):
        budget = int(csv.stem.replace(f"results_{dataset}_budget", ""))
        df = pd.read_csv(csv)
        for m in METHODS:
            rows.append({
                "budget": budget,
                "method": m,
                "aic_mean": df[f"{m}_aic"].mean(),
                "aic_ci": _ci95(df[f"{m}_aic"]),
                "f1_mean": df[f"{m}_f1"].mean(),
                "f1_ci": _ci95(df[f"{m}_f1"]),
            })
    if not rows:
        raise FileNotFoundError(f"No results/results_{dataset}_budget*.csv files found. Run sweep.py first.")
    return pd.DataFrame(rows)


def sweep_plots(dataset):
    summary = _load_all_budgets(dataset)
    out = Path("plots")
    out.mkdir(exist_ok=True)
    label_map = dict(zip(METHODS, LABELS))

    fig, ax = plt.subplots(figsize=(8, 5))
    for m, color in zip(METHODS, PALETTE):
        sub = summary[summary["method"] == m].sort_values("budget")
        ax.plot(sub["budget"], sub["aic_mean"], marker="o", color=color, label=label_map[m])
        ax.fill_between(sub["budget"], sub["aic_mean"] - sub["aic_ci"],
                         sub["aic_mean"] + sub["aic_ci"], color=color, alpha=0.15)
    ax.set_xlabel("Token Budget")
    ax.set_ylabel("Answer-in-Context Rate")
    ax.set_title(f"AIC Rate vs Token Budget ({dataset})", fontweight="bold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / f"fig9_aic_vs_budget_{dataset}.png", dpi=150)
    plt.close()
    print(f"  saved fig9_aic_vs_budget_{dataset}.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    for m, color in zip(METHODS, PALETTE):
        sub = summary[summary["method"] == m].sort_values("budget")
        ax.plot(sub["budget"], sub["f1_mean"], marker="o", color=color, label=label_map[m])
        ax.fill_between(sub["budget"], sub["f1_mean"] - sub["f1_ci"],
                         sub["f1_mean"] + sub["f1_ci"], color=color, alpha=0.15)
    ax.set_xlabel("Token Budget")
    ax.set_ylabel("Token F1")
    ax.set_title(f"F1 vs Token Budget ({dataset})", fontweight="bold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / f"fig10_f1_vs_budget_{dataset}.png", dpi=150)
    plt.close()
    print(f"  saved fig10_f1_vs_budget_{dataset}.png")

    budgets = sorted(summary["budget"].unique())
    pivot = summary.pivot(index="method", columns="budget", values="aic_mean").reindex(METHODS)
    pivot.index = LABELS
    fig, ax = plt.subplots(figsize=(1.2 * len(budgets) + 3, 4))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlGnBu", ax=ax, cbar_kws={"label": "AIC rate"})
    ax.set_title(f"AIC Rate: Method x Budget ({dataset})", fontweight="bold")
    ax.set_xlabel("Token Budget")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(out / f"fig11_heatmap_aic_{dataset}.png", dpi=150)
    plt.close()
    print(f"  saved fig11_heatmap_aic_{dataset}.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    baseline = summary[summary["method"] == "topk"].set_index("budget")["f1_mean"]
    for m, color in zip(METHODS, PALETTE):
        if m == "topk":
            continue
        sub = summary[summary["method"] == m].sort_values("budget")
        gain = sub.set_index("budget")["f1_mean"] - baseline
        ax.plot(gain.index, gain.values, marker="o", color=color, label=label_map[m])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Token Budget")
    ax.set_ylabel("Delta F1 over Top-K")
    ax.set_title(f"F1 Gain over Top-K Baseline vs Budget ({dataset})", fontweight="bold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / f"fig12_f1_gain_vs_budget_{dataset}.png", dpi=150)
    plt.close()
    print(f"  saved fig12_f1_gain_vs_budget_{dataset}.png")

    print(f"\nAll multi-budget plots for {dataset} written to {out}/")


def cross_dataset_plot(budget):
    """Compare AIC/F1 for AnswerSurvival's gain over Top-K across all evaluated datasets, at one budget."""
    results_dir = Path("results")
    rows = []
    for csv in sorted(results_dir.glob(f"results_*_budget{budget}.csv")):
        dataset = csv.stem.replace(f"_budget{budget}", "").replace("results_", "")
        df = pd.read_csv(csv)
        for m in METHODS:
            rows.append({
                "dataset": dataset, "method": m,
                "aic_mean": df[f"{m}_aic"].mean(),
                "f1_mean": df[f"{m}_f1"].mean(),
            })
    if not rows:
        raise FileNotFoundError(f"No results/results_*_budget{budget}.csv files found.")
    summary = pd.DataFrame(rows)
    datasets = sorted(summary["dataset"].unique())
    label_map = dict(zip(METHODS, LABELS))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x = np.arange(len(datasets))
    width = 0.8 / len(METHODS)
    for col, ax, ylabel in zip(["aic_mean", "f1_mean"], axes, ["AIC rate", "F1"]):
        for i, (m, color) in enumerate(zip(METHODS, PALETTE)):
            vals = [summary[(summary["dataset"] == d) & (summary["method"] == m)][col].mean() for d in datasets]
            ax.bar(x + i * width, vals, width=width, label=label_map[m], color=color, edgecolor="white")
        ax.set_xticks(x + width * (len(METHODS) - 1) / 2)
        ax.set_xticklabels(datasets, rotation=15)
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel)
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Cross-Dataset Comparison (budget={budget})", fontweight="bold")
    fig.tight_layout()
    out = Path("plots")
    out.mkdir(exist_ok=True)
    fig.savefig(out / f"fig14_cross_dataset_budget{budget}.png", dpi=150)
    plt.close()
    print(f"  saved fig14_cross_dataset_budget{budget}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="hotpotqa")
    parser.add_argument("--budget", type=int, default=160)
    parser.add_argument("--sweep", action="store_true",
                         help="Generate multi-budget comparison plots for --dataset.")
    parser.add_argument("--cross_dataset", action="store_true",
                         help="Generate cross-dataset comparison plot at --budget.")
    args = parser.parse_args()
    if args.cross_dataset:
        cross_dataset_plot(args.budget)
    elif args.sweep:
        sweep_plots(args.dataset)
    else:
        single_budget(args.dataset, args.budget)
