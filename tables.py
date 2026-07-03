"""
Render results/summary_*.csv into paper-ready markdown tables.

Usage:
  python tables.py
"""
from pathlib import Path

import pandas as pd

METHOD_LABEL = {"topk": "Top-K", "mmr": "MMR", "focused": "Focused", "answer_survival": "AnswerSurvival"}


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


def main():
    results = Path("results")
    metrics = pd.read_csv(results / "summary_metrics.csv")
    best = pd.read_csv(results / "summary_best_method.csv")
    sig_path = results / "summary_significance.csv"
    sig = pd.read_csv(sig_path) if sig_path.exists() else pd.DataFrame()

    parts = [main_metrics_table(metrics), best_method_table(best)]
    if not sig.empty:
        parts.append(significance_table(sig))

    out = Path("plots") / "results_tables.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
