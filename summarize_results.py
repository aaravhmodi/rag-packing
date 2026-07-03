"""
Consolidate every results_*.csv and significance_*.csv into one paper-ready summary table.

Usage:
  python summarize_results.py
"""
from pathlib import Path

import pandas as pd

METHODS = ["topk", "mmr", "focused", "answer_survival"]


def build_metrics_table():
    rows = []
    for csv in sorted(Path("results").glob("results_*_budget*.csv")):
        stem = csv.stem[len("results_"):]
        dataset, _, budget_str = stem.rpartition("_budget")
        budget = int(budget_str)
        df = pd.read_csv(csv)
        for m in METHODS:
            rows.append({
                "dataset": dataset,
                "budget": budget,
                "method": m,
                "n": len(df),
                "aic": df[f"{m}_aic"].mean(),
                "f1": df[f"{m}_f1"].mean(),
                "em": df[f"{m}_em"].mean(),
                "tokens": df[f"{m}_tokens"].mean(),
            })
    return pd.DataFrame(rows)


def build_significance_table():
    rows = []
    for csv in sorted(Path("results").glob("significance_*_budget*.csv")):
        stem = csv.stem[len("significance_"):]
        dataset, _, budget_str = stem.rpartition("_budget")
        budget = int(budget_str)
        df = pd.read_csv(csv)
        df.insert(0, "budget", budget)
        df.insert(0, "dataset", dataset)
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def main():
    metrics = build_metrics_table()
    sig = build_significance_table()

    out_dir = Path("results")
    metrics_path = out_dir / "summary_metrics.csv"
    sig_path = out_dir / "summary_significance.csv"
    metrics.to_csv(metrics_path, index=False)
    if not sig.empty:
        sig.to_csv(sig_path, index=False)

    # Best method per dataset/budget by AIC and F1
    best = []
    for (dataset, budget), group in metrics.groupby(["dataset", "budget"]):
        best_aic = group.loc[group["aic"].idxmax()]
        best_f1 = group.loc[group["f1"].idxmax()]
        best.append({
            "dataset": dataset, "budget": budget,
            "best_aic_method": best_aic["method"], "best_aic": best_aic["aic"],
            "as_aic": group[group["method"] == "answer_survival"]["aic"].iloc[0],
            "best_f1_method": best_f1["method"], "best_f1": best_f1["f1"],
            "as_f1": group[group["method"] == "answer_survival"]["f1"].iloc[0],
        })
    best_df = pd.DataFrame(best).sort_values(["dataset", "budget"])
    best_path = out_dir / "summary_best_method.csv"
    best_df.to_csv(best_path, index=False)

    print(f"Wrote {metrics_path} ({len(metrics)} rows)")
    if not sig.empty:
        print(f"Wrote {sig_path} ({len(sig)} rows)")
    print(f"Wrote {best_path} ({len(best_df)} rows)")

    print("\n=== Where does AnswerSurvival win on AIC? ===")
    wins = best_df[best_df["best_aic_method"] == "answer_survival"]
    print(wins[["dataset", "budget", "as_aic"]].to_string(index=False) if not wins.empty else "  (none)")

    if not sig.empty:
        print("\n=== Statistically significant AnswerSurvival F1 differences (95% CI excludes 0) ===")
        sig_hits = sig[(sig["metric"] == "f1") & (sig["significant_95"])]
        if sig_hits.empty:
            print("  (none)")
        else:
            print(sig_hits[["dataset", "budget", "baseline", "mean_diff", "p_value"]].to_string(index=False))


if __name__ == "__main__":
    main()
