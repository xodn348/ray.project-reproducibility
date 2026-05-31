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


def read_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise SystemExit(f"missing address-level summary: {path}")
    return pd.read_csv(path)


def main() -> int:
    coverage = json.loads((DATA_DIR / "coverage_summary.json").read_text())
    address_total = float(coverage["address_axis"]["address_count"])
    balance_total = float(coverage["balance_axis"]["address_attributable_btc"])

    dormancy = read_csv("dormancy_balance.csv")
    dormancy["address_count"] = pd.to_numeric(dormancy["address_count"])
    dormancy["balance_btc"] = pd.to_numeric(dormancy["balance_btc"])
    recent_mask = dormancy["dormancy_class"].isin(["active", "recent"])
    recency = pd.DataFrame(
        [
            {
                "class": "<1y current-output\naddress",
                "addresses": dormancy.loc[recent_mask, "address_count"].sum(),
                "btc": dormancy.loc[recent_mask, "balance_btc"].sum(),
            },
            {
                "class": ">=1y current-output\naddress",
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
    top_balance["current_balance_btc"] = pd.to_numeric(top_balance["current_balance_btc"])
    top_utxo["current_balance_btc"] = pd.to_numeric(top_utxo["current_balance_btc"])
    top_utxo["n_unspent_utxos"] = pd.to_numeric(top_utxo["n_unspent_utxos"])
    concentration = pd.DataFrame(
        [
            {
                "label": "Top 10\nbalance",
                "btc_share": top_balance.head(10)["current_balance_btc"].sum() / balance_total,
                "utxo_share": None,
            },
            {
                "label": "Top 100\nbalance",
                "btc_share": top_balance.head(100)["current_balance_btc"].sum() / balance_total,
                "utxo_share": None,
            },
            {
                "label": "Top 10\nUTXO-count",
                "btc_share": top_utxo.head(10)["current_balance_btc"].sum() / balance_total,
                "utxo_share": top_utxo.head(10)["n_unspent_utxos"].sum() / float(coverage["balance_axis"]["utxo_rows"]),
            },
            {
                "label": "Top 100\nUTXO-count",
                "btc_share": top_utxo.head(100)["current_balance_btc"].sum() / balance_total,
                "utxo_share": top_utxo.head(100)["n_unspent_utxos"].sum() / float(coverage["balance_axis"]["utxo_rows"]),
            },
        ]
    )

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )
    fig, axs = plt.subplots(1, 3, figsize=(14.2, 4.3))

    ax = axs[0]
    x = range(len(recency))
    width = 0.35
    ax.bar([i - width / 2 for i in x], recency["address_share"] * 100, width, label="Address share", color="#2563eb")
    ax.bar([i + width / 2 for i in x], recency["btc_share"] * 100, width, label="BTC share", color="#c2410c")
    ax.set_xticks(list(x), recency["class"].astype(str))
    for i, row in recency.iterrows():
        ax.text(
            i - width / 2,
            row["address_share"] * 100 + 2.0,
            f"{row['address_share'] * 100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#1e3a8a",
        )
        ax.text(
            i + width / 2,
            row["btc_share"] * 100 + 2.0,
            f"{row['btc_share'] * 100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#7c2d12",
        )
    ax.set_ylim(0, 92)
    ax.set_title("A. 20.7% of addresses hold 82.2% of BTC", pad=28)
    ax.set_ylabel("Share of address-attributable set (%)")
    ax.legend(
        frameon=True,
        facecolor="white",
        edgecolor="#cbd5e1",
        fontsize=8,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.03),
        ncol=2,
    )
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)

    ax = axs[1]
    x = range(len(freq))
    ax.plot(list(x), freq["address_share"] * 100, marker="o", label="Address share", color="#7c3aed")
    ax.plot(list(x), freq["btc_share"] * 100, marker="s", label="BTC share", color="#0f766e")
    ax.set_xticks(list(x), freq["n_unspent_utxos_bucket"].astype(str), rotation=0)
    ax.set_title("B. Address count and BTC share diverge")
    ax.set_xlabel("Current UTXOs at address")
    ax.set_ylabel("Share (%)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)

    ax = axs[2]
    x = range(len(concentration))
    ax.bar(list(x), concentration["btc_share"] * 100, color="#dc2626", label="BTC share")
    for i, v in enumerate(concentration["utxo_share"]):
        if pd.notna(v):
            ax.scatter(i, v * 100, color="#111827", s=42, label="UTXO share" if i == 2 else None, zorder=3)
    ax.set_xticks(list(x), concentration["label"].astype(str))
    ax.set_title("C. Value tail differs from output-count tail")
    ax.set_ylabel("Share (%)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)

    fig.tight_layout(rect=(0, 0, 1, 0.95))

    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig06_address_one_year.{ext}"
        fig.savefig(out, dpi=150 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
