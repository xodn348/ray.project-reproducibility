# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""Cumulative unspent BTC age thresholds from local Bitcoin Core snapshot."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "phase2" / "utxo_snapshot_20260523" / "utxo_cumulative_age.csv"
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    if not DATA.exists():
        raise SystemExit(f"missing local UTXO snapshot aggregate: {DATA}")
    df = pd.read_csv(DATA)
    df["share_pct"] = pd.to_numeric(df["share_of_total_btc"], errors="coerce").astype(float) * 100.0
    df["total_btc_m"] = pd.to_numeric(df["total_btc"], errors="coerce").astype(float) / 1_000_000.0
    labels = df["threshold"].astype(str).str.replace(">=", ">=", regex=False).tolist()

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 18,
        "axes.labelsize": 15,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
    })
    fig, ax = plt.subplots(figsize=(13.2, 6.8))
    ax.plot(labels, df["share_pct"], color="#0f766e", linewidth=2.8, marker="o", markersize=8)
    ax.fill_between(range(len(labels)), df["share_pct"].to_numpy(dtype=float), color="#99f6e4", alpha=0.35)
    ax.set_ylabel("BTC still unspent at or above threshold (%)")
    ax.set_xlabel("Minimum UTXO age threshold")
    ax.set_ylim(0, 105)
    ax.grid(True, axis="y", linestyle=":", linewidth=0.7, alpha=0.55)
    ax.tick_params(axis="x", rotation=25)
    for i, row in df.iterrows():
        ax.text(i, float(row["share_pct"]) + 2.0, f"{float(row['share_pct']):.1f}%", ha="center", fontsize=11)
    fig.suptitle("Current BTC unspent past age thresholds", fontsize=18, y=0.99)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig04_sink_lens.{ext}"
        fig.savefig(out, dpi=150 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
