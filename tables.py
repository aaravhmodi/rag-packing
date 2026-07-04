"""
Render results/summary_*.csv into paper-ready markdown tables.

Usage:
  python tables.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

METHOD_LABEL = {"topk": "Top-K", "mmr": "MMR", "focused": "Focused", "answer_survival": "AnswerSurvival"}
HEADER_COLOR = "#2c3e50"
HEADER_TEXT = "white"
ROW_COLORS = ("#f7f7f7", "#ffffff")
AS_ROW_TINT = "#fbe9f2"  # light tint to make the AnswerSurvival row easy to scan
BOLD_COLOR = "#1a7a1a"


def render_table_png(rows, col_labels, out_path, title, bold_mask=None, row_tint=None,
                      col_widths=None, fontsize=10):
    """
    rows: list[list[str]] cell text
    bold_mask: set of (row_idx, col_idx) to render bold+green (marks a "best"/winning cell)
    row_tint: dict[row_idx] -> hex color to tint that whole row
    """
    bold_mask = bold_mask or set()
    row_tint = row_tint or {}
    n_rows, n_cols = len(rows), len(col_labels)

    fig_w = max(6, sum(col_widths) if col_widths else n_cols * 1.6)
    fig_h = 0.32 * (n_rows + 1) + 0.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    ax.set_title(title, fontweight="bold", fontsize=13, y=1.0 + 0.4 / fig_h)

    table = ax.table(cellText=rows, colLabels=col_labels, cellLoc="center", loc="center",
                      colWidths=col_widths, bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)

    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if r == 0:
            cell.set_facecolor(HEADER_COLOR)
            cell.set_text_props(color=HEADER_TEXT, fontweight="bold")
        else:
            data_row = r - 1
            base = row_tint.get(data_row, ROW_COLORS[data_row % 2])
            cell.set_facecolor(base)
            if (data_row, c) in bold_mask:
                cell.set_text_props(color=BOLD_COLOR, fontweight="bold")

    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out_path.name}")


def _bold_best(vals, fmt="{:.3f}"):
    """Return formatted strings with the max value bolded."""
    best = max(vals)
    return [f"**{fmt.format(v)}**" if v == best else fmt.format(v) for v in vals]


def main_metrics_table(metrics: pd.DataFrame) -> str:
    lines = ["## Main Results: AIC / F1 / EM by Dataset and Budget\n"]
    lines.append("Bold = best value in that row group (dataset x budget).\n")
    for dataset, group in metrics.groupby("dataset"):
        lines.append(f"\n### {dataset}\n")
        lines.append("| Budget | Method | AIC | F1 | EM | Avg Tokens |")
        lines.append("|---|---|---|---|---|---|")
        for budget, sub in group.groupby("budget"):
            sub = sub.set_index("method").loc[["topk", "mmr", "focused", "answer_survival"]]
            aic_fmt = _bold_best(sub["aic"].tolist())
            f1_fmt = _bold_best(sub["f1"].tolist())
            em_fmt = _bold_best(sub["em"].tolist())
            for i, method in enumerate(sub.index):
                b = str(budget) if i == 0 else ""
                lines.append(
                    f"| {b} | {METHOD_LABEL[method]} | {aic_fmt[i]} | {f1_fmt[i]} | "
                    f"{em_fmt[i]} | {sub['tokens'].iloc[i]:.1f} |"
                )
    return "\n".join(lines)


def best_method_table(best: pd.DataFrame) -> str:
    lines = ["\n\n## Best Method per Dataset/Budget\n"]
    lines.append("| Dataset | Budget | Best AIC method | Best AIC | AnswerSurvival AIC | "
                  "Best F1 method | Best F1 | AnswerSurvival F1 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for _, r in best.sort_values(["dataset", "budget"]).iterrows():
        aic_mark = " <- AS wins" if r["best_aic_method"] == "answer_survival" else ""
        f1_mark = " <- AS wins" if r["best_f1_method"] == "answer_survival" else ""
        lines.append(
            f"| {r['dataset']} | {r['budget']} | {METHOD_LABEL[r['best_aic_method']]}{aic_mark} | "
            f"{r['best_aic']:.3f} | {r['as_aic']:.3f} | {METHOD_LABEL[r['best_f1_method']]}{f1_mark} | "
            f"{r['best_f1']:.3f} | {r['as_f1']:.3f} |"
        )
    return "\n".join(lines)


def significance_table(sig: pd.DataFrame) -> str:
    lines = ["\n\n## Statistical Significance: AnswerSurvival vs Baselines (paired bootstrap, 95% CI)\n"]
    lines.append("Only rows with a significant difference (CI excludes 0) shown. "
                  "Positive mean_diff = AnswerSurvival better.\n")
    sig_hits = sig[sig["significant_95"]].copy()
    if sig_hits.empty:
        lines.append("\n*No statistically significant differences at the 95% level in this run.*")
        return "\n".join(lines)
    sig_hits["direction"] = sig_hits["mean_diff"].apply(lambda d: "AS better" if d > 0 else "AS worse")
    lines.append("| Dataset | Budget | Metric | Baseline | Mean diff | 95% CI | p-value | Direction |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for _, r in sig_hits.sort_values(["dataset", "budget", "metric"]).iterrows():
        ci = f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}]"
        lines.append(
            f"| {r['dataset']} | {r['budget']} | {r['metric']} | {METHOD_LABEL[r['baseline']]} | "
            f"{r['mean_diff']:+.3f} | {ci} | {r['p_value']:.4f} | {r['direction']} |"
        )
    return "\n".join(lines)


def png_main_metrics_table(metrics: pd.DataFrame, dataset: str, out_dir: Path):
    group = metrics[metrics["dataset"] == dataset]
    col_labels = ["Budget", "Method", "AIC", "F1", "EM", "Avg Tokens"]
    rows, bold_mask, row_tint = [], set(), {}
    r = 0
    for budget, sub in group.groupby("budget"):
        sub = sub.set_index("method").loc[["topk", "mmr", "focused", "answer_survival"]]
        best_aic, best_f1, best_em = sub["aic"].max(), sub["f1"].max(), sub["em"].max()
        for i, method in enumerate(sub.index):
            row = [
                str(budget) if i == 0 else "",
                METHOD_LABEL[method],
                f"{sub['aic'].iloc[i]:.3f}",
                f"{sub['f1'].iloc[i]:.3f}",
                f"{sub['em'].iloc[i]:.3f}",
                f"{sub['tokens'].iloc[i]:.1f}",
            ]
            if sub["aic"].iloc[i] == best_aic:
                bold_mask.add((r, 2))
            if sub["f1"].iloc[i] == best_f1:
                bold_mask.add((r, 3))
            if sub["em"].iloc[i] == best_em:
                bold_mask.add((r, 4))
            if method == "answer_survival":
                row_tint[r] = AS_ROW_TINT
            rows.append(row)
            r += 1
    render_table_png(
        rows, col_labels, out_dir / f"table_results_{dataset}.png",
        f"Results: {dataset}  (bold = best in group, pink row = AnswerSurvival)",
        bold_mask=bold_mask, row_tint=row_tint,
        col_widths=[0.7, 1.4, 0.8, 0.8, 0.8, 1.0],
    )


def png_best_method_table(best: pd.DataFrame, out_dir: Path):
    col_labels = ["Dataset", "Budget", "Best AIC", "AIC", "AS AIC", "Best F1", "F1", "AS F1"]
    rows, bold_mask, row_tint = [], set(), {}
    for r, (_, row) in enumerate(best.sort_values(["dataset", "budget"]).iterrows()):
        as_wins_aic = row["best_aic_method"] == "answer_survival"
        as_wins_f1 = row["best_f1_method"] == "answer_survival"
        rows.append([
            row["dataset"], str(row["budget"]),
            METHOD_LABEL[row["best_aic_method"]], f"{row['best_aic']:.3f}", f"{row['as_aic']:.3f}",
            METHOD_LABEL[row["best_f1_method"]], f"{row['best_f1']:.3f}", f"{row['as_f1']:.3f}",
        ])
        if as_wins_aic:
            bold_mask.add((r, 2))
            row_tint[r] = AS_ROW_TINT
        if as_wins_f1:
            bold_mask.add((r, 5))
            row_tint[r] = AS_ROW_TINT
    render_table_png(
        rows, col_labels, out_dir / "table_best_method.png",
        "Best Method per Dataset/Budget (pink row = AnswerSurvival wins AIC and/or F1)",
        bold_mask=bold_mask, row_tint=row_tint,
        col_widths=[1.5, 0.7, 1.1, 0.7, 0.8, 1.1, 0.7, 0.8],
        fontsize=9,
    )


def png_significance_table(sig: pd.DataFrame, out_dir: Path):
    sig_hits = sig[sig["significant_95"]].copy()
    if sig_hits.empty:
        return
    sig_hits["direction"] = sig_hits["mean_diff"].apply(lambda d: "AS better" if d > 0 else "AS worse")
    sig_hits = sig_hits.sort_values(["dataset", "budget", "metric"])

    col_labels = ["Dataset", "Budget", "Metric", "Baseline", "Mean diff", "95% CI", "p", "Direction"]
    rows, bold_mask, row_tint = [], set(), {}
    for r, (_, row) in enumerate(sig_hits.iterrows()):
        ci = f"[{row['ci_low']:+.3f}, {row['ci_high']:+.3f}]"
        rows.append([
            row["dataset"], str(row["budget"]), row["metric"], METHOD_LABEL[row["baseline"]],
            f"{row['mean_diff']:+.3f}", ci, f"{row['p_value']:.4f}", row["direction"],
        ])
        if row["direction"] == "AS better":
            bold_mask.add((r, 7))
            row_tint[r] = "#e8f7e8"
        else:
            row_tint[r] = "#fdeaea"
    render_table_png(
        rows, col_labels, out_dir / "table_significance.png",
        "Statistically Significant Differences (95% paired bootstrap CI excludes 0)",
        bold_mask=bold_mask, row_tint=row_tint,
        col_widths=[1.5, 0.7, 0.7, 1.0, 0.9, 1.3, 0.7, 0.9],
        fontsize=9,
    )


def main():
    results = Path("results")
    metrics = pd.read_csv(results / "summary_metrics.csv")
    best = pd.read_csv(results / "summary_best_method.csv")
    sig_path = results / "summary_significance.csv"
    sig = pd.read_csv(sig_path) if sig_path.exists() else pd.DataFrame()

    parts = [main_metrics_table(metrics), best_method_table(best)]
    if not sig.empty:
        parts.append(significance_table(sig))

    out_dir = Path("plots")
    out_dir.mkdir(exist_ok=True)
    md_out = out_dir / "results_tables.md"
    md_out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Saved -> {md_out}")

    for dataset in sorted(metrics["dataset"].unique()):
        png_main_metrics_table(metrics, dataset, out_dir)
    png_best_method_table(best, out_dir)
    if not sig.empty:
        png_significance_table(sig, out_dir)


if __name__ == "__main__":
    main()
