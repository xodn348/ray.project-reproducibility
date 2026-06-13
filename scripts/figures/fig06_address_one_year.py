# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""One-year address-level recency checks from chainstate summaries."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "phase2" / "address_core_stage1"
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ADDRESS_BLUE = "#60a5fa"
BTC_ORANGE = "#ea580c"
AUX_GRAY = "#64748b"
DARK_BLUE = "#1e3a8a"
DARK_ORANGE = "#9a3412"
DARK_GRAY = "#475569"


def read_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise SystemExit(f"missing address-level summary: {path}")
    return pd.read_csv(path)


def label_bars(ax, bars, fmt="{:.1f}%", dy=1.2, fontsize=10, color="#111827", min_value=0.0):
    for bar in bars:
        h = bar.get_height()
        if h < min_value:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + dy,
            fmt.format(h),
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color=color,
        )


def main() -> int:
    coverage = json.loads((DATA_DIR / "coverage_summary.json").read_text())
    address_total = float(coverage["address_axis"]["address_count"])
    balance_total = float(coverage["balance_axis"]["address_attributable_btc"])
    utxo_total = float(coverage["balance_axis"]["utxo_rows"])

    dormancy = read_csv("dormancy_balance.csv")
    dormancy["address_count"] = pd.to_numeric(dormancy["address_count"])
    dormancy["balance_btc"] = pd.to_numeric(dormancy["balance_btc"])
    recent_mask = dormancy["dormancy_class"].isin(["active", "recent", "dormant_1y", "dormant_3y"])
    recency = pd.DataFrame(
        [
            {
                "class": "Newest UTXO\n<5 years",
                "addresses": dormancy.loc[recent_mask, "address_count"].sum(),
                "btc": dormancy.loc[recent_mask, "balance_btc"].sum(),
            },
            {
                "class": "Newest UTXO\n≥5 years",
                "addresses": dormancy.loc[~recent_mask, "address_count"].sum(),
                "btc": dormancy.loc[~recent_mask, "balance_btc"].sum(),
            },
        ]
    )
    recency["address_share"] = recency["addresses"] / address_total
    recency["btc_share"] = recency["btc"] / balance_total

    freq = read_csv("utxo_count_distribution.csv")
    freq["address_count"] = pd.to_numeric(freq["address_count"])
    freq["balance_btc"] = pd.to_numeric(freq["balance_btc"])
    freq["address_share"] = freq["address_count"] / address_total
    freq["btc_share"] = freq["balance_btc"] / balance_total

    top_balance = read_csv("top_balance.csv")
    top_utxo = read_csv("top_utxo_count.csv")
    for df in (top_balance, top_utxo):
        df["current_balance_btc"] = pd.to_numeric(df["current_balance_btc"])
        df["n_unspent_utxos"] = pd.to_numeric(df["n_unspent_utxos"])
    concentration = pd.DataFrame(
        [
            {
                "label": "Top 100\nby BTC balance",
                "btc_share": top_balance.head(100)["current_balance_btc"].sum() / balance_total,
                "utxo_share": top_balance.head(100)["n_unspent_utxos"].sum() / utxo_total,
            },
            {
                "label": "Top 100\nby UTXO count",
                "btc_share": top_utxo.head(100)["current_balance_btc"].sum() / balance_total,
                "utxo_share": top_utxo.head(100)["n_unspent_utxos"].sum() / utxo_total,
            },
        ]
    )

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.axisbelow": True,
            "axes.titlesize": 15,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
        }
    )
    fig, axs = plt.subplots(1, 3, figsize=(15.7, 5.35))

    ax = axs[0]
    x = list(range(len(recency)))
    width = 0.36
    b1 = ax.bar([i - width / 2 for i in x], recency["address_share"] * 100, width, label="Address share", color=ADDRESS_BLUE)
    b2 = ax.bar([i + width / 2 for i in x], recency["btc_share"] * 100, width, label="BTC share", color=BTC_ORANGE)
    ax.set_xticks(x, recency["class"].astype(str))
    label_bars(ax, b1, fontsize=10, color=DARK_BLUE)
    label_bars(ax, b2, fontsize=10, color=DARK_ORANGE)
    ax.set_ylim(0, 100)
    ax.set_title("A. Address recency and BTC share", pad=14)
    ax.set_ylabel("Share of address-attributable set (%)")
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)

    ax = axs[1]
    x = list(range(len(freq)))
    width = 0.38
    b1 = ax.bar([i - width / 2 for i in x], freq["address_share"] * 100, width, label="Address share", color=ADDRESS_BLUE)
    b2 = ax.bar([i + width / 2 for i in x], freq["btc_share"] * 100, width, label="BTC share", color=BTC_ORANGE)
    ax.set_xticks(x, freq["n_unspent_utxos_bucket"].astype(str), rotation=22, ha="right")
    ax.set_title("B. Current UTXOs per address", pad=14)
    ax.set_xlabel("Current UTXOs at address")
    ax.set_ylabel("Share (%)")
    ax.legend(frameon=False, fontsize=10)
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)

    ax = axs[2]
    # One bar per top-100 list, centered on its tick: the BTC-balance list is
    # read on the BTC-share axis and the UTXO-count list on the UTXO-share axis,
    # matching the two measurements quoted in the text.
    width = 0.36
    b1 = ax.bar([0], concentration.loc[0, "btc_share"] * 100, width, label="BTC share", color=BTC_ORANGE)
    b2 = ax.bar([1], concentration.loc[1, "utxo_share"] * 100, width, label="UTXO-count share", color=AUX_GRAY)
    ax.set_xticks([0, 1], concentration["label"].astype(str))
    ax.set_xlim(-0.7, 1.7)
    label_bars(ax, b1, fontsize=10, color=DARK_ORANGE, min_value=0.5)
    label_bars(ax, b2, fontsize=10, color=DARK_GRAY, min_value=0.5)
    ax.set_ylim(0, max((concentration["btc_share"] * 100).max(), (concentration["utxo_share"] * 100).max()) + 4.5)
    ax.set_title("C. Top-100 balance and UTXO-count shares", pad=14)
    ax.set_ylabel("Share (%)")
    ax.legend(frameon=False, fontsize=10)
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)

    fig.tight_layout(w_pad=2.0)

    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig06_address_one_year.{ext}"
        fig.savefig(out, dpi=170 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
