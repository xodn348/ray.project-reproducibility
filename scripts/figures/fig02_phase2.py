# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""UTXO age distribution from local Bitcoin Core dumptxoutset snapshot."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "phase2" / "utxo_snapshot_20260523" / "utxo_age_buckets.csv"
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    if not DATA.exists():
        raise SystemExit(f"missing local UTXO snapshot aggregate: {DATA}")
    df = pd.read_csv(DATA)
    df["share_pct"] = pd.to_numeric(df["share_of_total_btc"], errors="coerce").astype(float) * 100.0
    df["total_btc_m"] = pd.to_numeric(df["total_btc"], errors="coerce").astype(float) / 1_000_000.0
    labels = df["bucket"].astype(str).tolist()

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.axisbelow": True,
        "axes.titlesize": 18,
        "axes.labelsize": 15,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
    })
    fig, ax = plt.subplots(figsize=(13.5, 7.2))
    colors = ["#dbeafe", "#bfdbfe", "#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#1e40af", "#1e3a8a", "#172554"]
    bars = ax.bar(labels, df["share_pct"], color=colors, edgecolor="#0f172a", linewidth=0.4)
    ax.set_ylabel("Share of current UTXO-set BTC (%)")
    ax.set_xlabel("Age since creating transaction, height-based approximation")
    ax.set_ylim(0, max(36, float(df["share_pct"].max()) * 1.18))
    ax.grid(True, axis="y", linestyle=":", linewidth=0.7, alpha=0.55)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    for bar, btc_m in zip(bars, df["total_btc_m"], strict=False):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.7,
                f"{bar.get_height():.1f}%\n{btc_m:.2f}M", ha="center", va="bottom", fontsize=11)
    one_plus = df.loc[df["bucket"].isin(["1-2 years", "2-3 years", "3-5 years", ">5 years"]), "share_pct"].sum()
    three_plus = df.loc[df["bucket"].isin(["3-5 years", ">5 years"]), "share_pct"].sum()
    ax.text(0.02, 0.96, f"Local dumptxoutset snapshot, height 950,696\n≥1y: {one_plus:.1f}% of BTC; ≥3y: {three_plus:.1f}%",
            transform=ax.transAxes, ha="left", va="top", fontsize=13,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#64748b", alpha=0.94))
    fig.suptitle("UTXO snapshot age distribution", fontsize=18, y=0.99)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig02_stock_lens.{ext}"
        fig.savefig(out, dpi=150 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
