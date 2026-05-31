# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""Top-100 address concentration checks from committed summaries."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "phase2" / "address_core_stage1"
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def pct(value: float) -> float:
    return value * 100.0


def label_pct(value: float) -> str:
    return "" if 0 < value < 0.1 else f"{value:.1f}%"


def main() -> int:
    coverage = json.loads((DATA_DIR / "coverage_summary.json").read_text())
    balance_total = float(coverage["balance_axis"]["address_attributable_btc"])
    utxo_total = float(coverage["balance_axis"]["utxo_rows"])

    top_balance = pd.read_csv(DATA_DIR / "top_balance.csv")
    top_utxo = pd.read_csv(DATA_DIR / "top_utxo_count.csv")
    for frame in (top_balance, top_utxo):
        frame["current_balance_btc"] = pd.to_numeric(frame["current_balance_btc"])
        frame["n_unspent_utxos"] = pd.to_numeric(frame["n_unspent_utxos"])

    rows = [
        {
            "group": "Top 100\nby BTC balance",
            "BTC share": pct(top_balance.head(100)["current_balance_btc"].sum() / balance_total),
            "UTXO count share": pct(top_balance.head(100)["n_unspent_utxos"].sum() / utxo_total),
        },
        {
            "group": "Top 100\nby UTXO count",
            "BTC share": pct(top_utxo.head(100)["current_balance_btc"].sum() / balance_total),
            "UTXO count share": pct(top_utxo.head(100)["n_unspent_utxos"].sum() / utxo_total),
        },
    ]
    data = pd.DataFrame(rows)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 9,
        }
    )
    fig, ax = plt.subplots(1, 1, figsize=(8.4, 4.1))

    x = list(range(len(data)))
    width = 0.32
    btc_vals = data["BTC share"].tolist()
    utxo_vals = data["UTXO count share"].tolist()
    bars_btc = ax.bar(
        [i - width / 2 for i in x],
        btc_vals,
        width,
        color="#dc2626",
        label="BTC balance share",
    )
    bars_utxo = ax.bar(
        [i + width / 2 for i in x],
        utxo_vals,
        width,
        color="#1d4ed8",
        label="UTXO count share",
    )

    for bar, value in zip([*bars_btc, *bars_utxo], [*btc_vals, *utxo_vals], strict=True):
        y = value if value >= 0.1 else 0.18
        label = label_pct(value)
        if not label:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y + 0.35,
            label,
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold" if value >= 1 else "normal",
            color="#0f172a",
        )

    ax.set_xticks(x, data["group"].tolist())
    ax.set_ylim(0, 18.5)
    ax.set_ylabel("Share of address-attributable total (%)")
    ax.set_title("Top-100 address groups: BTC value share vs UTXO count share")
    ax.legend(
        frameon=True,
        facecolor="white",
        edgecolor="#cbd5e1",
        loc="upper right",
        ncol=2,
        fontsize=9,
    )
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)
    fig.tight_layout()

    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig07_address_rank_profiles.{ext}"
        fig.savefig(out, dpi=150 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
