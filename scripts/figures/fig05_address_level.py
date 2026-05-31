# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
"""Script-protocol and address-level summary figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "phase2" / "address_core_stage1"
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COUNT_BLUE = "#60a5fa"
VALUE_ORANGE = "#ea580c"
DARK_ORANGE = "#9a3412"


def read_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise SystemExit(f"missing address-level summary: {path}")
    return pd.read_csv(path)


def main() -> int:
    coverage_path = DATA_DIR / "coverage_summary.json"
    if not coverage_path.exists():
        raise SystemExit(f"missing address-level coverage summary: {coverage_path}")

    script = read_csv("script_type_balance.csv")
    freq = read_csv("utxo_count_distribution.csv")
    top_balance = read_csv("top_balance.csv")
    script["utxo_count"] = pd.to_numeric(script["utxo_count"], errors="coerce").fillna(0)
    script["balance_btc"] = pd.to_numeric(script["balance_btc"], errors="coerce").fillna(0.0)
    script["utxo_share"] = script["utxo_count"] / script["utxo_count"].sum() * 100.0
    script["btc_share"] = script["balance_btc"] / script["balance_btc"].sum() * 100.0
    order = ["p2wpkh", "p2pkh", "p2sh", "p2pk", "p2wsh", "p2tr", "multisig", "other"]
    script["_order"] = script["script_type"].map({k: i for i, k in enumerate(order)}).fillna(99)
    script = script.sort_values("_order")

    freq["address_count"] = (
        pd.to_numeric(freq["address_count"], errors="coerce").fillna(0).astype(int)
    )
    freq["balance_btc"] = pd.to_numeric(freq["balance_btc"], errors="coerce").fillna(
        0.0
    )
    top_balance["current_balance_btc"] = pd.to_numeric(
        top_balance["current_balance_btc"], errors="coerce"
    ).fillna(0.0)

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
    fig, ax = plt.subplots(1, 1, figsize=(8.6, 4.2))
    x = list(range(len(script)))
    width = 0.36
    ax.bar(
        [i - width / 2 for i in x],
        script["utxo_share"],
        width,
        color=COUNT_BLUE,
        label="UTXO count share",
    )
    ax.bar(
        [i + width / 2 for i in x],
        script["btc_share"],
        width,
        color=VALUE_ORANGE,
        label="BTC balance share",
    )
    ax.set_xticks(x, script["script_type"].astype(str), rotation=25)
    ax.set_title("Script families: UTXO count vs BTC balance")
    ax.set_ylabel("Share of current UTXO set (%)")
    ax.legend(
        frameon=True,
        facecolor="white",
        edgecolor="#cbd5e1",
        fontsize=8,
        loc="upper right",
    )
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig05_script_family_mix.{ext}"
        fig.savefig(out, dpi=150 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)

    fig, ax = plt.subplots(1, 1, figsize=(8.6, 4.2))
    avg = script.copy()
    avg["btc_per_utxo"] = avg["balance_btc"] / avg["utxo_count"].clip(lower=1)
    ax.bar(avg["script_type"].astype(str), avg["btc_per_utxo"], color=VALUE_ORANGE)
    ax.set_yscale("log")
    ax.set_title("Average BTC per current UTXO by script family")
    ax.set_ylabel("BTC per current UTXO, log scale")
    ax.set_xlabel("Script family")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(True, which="both", axis="y", linestyle=":", alpha=0.45)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig06_script_value_per_utxo.{ext}"
        fig.savefig(out, dpi=150 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(12.8, 4.4))

    ax = axs[0]
    ax.bar(
        freq["n_unspent_utxos_bucket"].astype(str),
        freq["address_count"] / 1_000_000.0,
        color=COUNT_BLUE,
    )
    single = freq.iloc[0]
    ax.text(
        0.98,
        0.92,
        f"1-UTXO addresses:\n{single['address_count'] / freq['address_count'].sum() * 100:.1f}% of addresses\n{single['balance_btc'] / freq['balance_btc'].sum() * 100:.1f}% of BTC",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10,
        color="#0f172a",
        bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": "#cbd5e1"},
    )
    ax.set_title("A. Most addresses have one current UTXO")
    ax.set_ylabel("Addresses (millions)")
    ax.set_xlabel("Unspent UTXOs at address")
    ax.grid(True, axis="y", linestyle=":", alpha=0.45)

    ax = axs[1]
    top = top_balance.head(10).copy()
    x = range(1, len(top) + 1)
    ax.plot(
        list(x), top["current_balance_btc"], marker="o", linewidth=2.0, color=DARK_ORANGE
    )
    top10_btc = top_balance.head(10)["current_balance_btc"].sum()
    top100_btc = top_balance.head(100)["current_balance_btc"].sum()
    ax.text(
        0.98,
        0.92,
        f"Top 10: {top10_btc / 1_000_000:.2f}M BTC\nTop 100: {top100_btc / 1_000_000:.2f}M BTC",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10,
        color="#0f172a",
        bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": "#cbd5e1"},
    )
    ax.set_yscale("log")
    ax.set_title("B. Top balances dwarf ordinary address balances")
    ax.set_ylabel("BTC, log scale")
    ax.set_xlabel("Rank")
    ax.grid(True, which="both", axis="y", linestyle=":", alpha=0.45)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig05_address_count_rank.{ext}"
        fig.savefig(out, dpi=150 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
