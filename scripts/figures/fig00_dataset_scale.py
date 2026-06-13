# pyright: reportAttributeAccessIssue=false
"""Dataset-scale banner: funded addresses, UTXO-set BTC, analyzed transactions."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PHASE2_DIR = ROOT / "data" / "phase2"
ADDRESS_DIR = PHASE2_DIR / "address_core_stage1"
SNAPSHOT_DIR = PHASE2_DIR / "utxo_snapshot_20260523"
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DARK_BLUE = "#1e3a8a"
DARK_ORANGE = "#9a3412"
DARK_GRAY = "#475569"
LABEL_GRAY = "#64748b"
SEPARATOR_GRAY = "#cbd5e1"


def _find_flow_blocks_csv() -> Path:
    fullnode_dirs = sorted(PHASE2_DIR.glob("rpc_retained_flow_fullnode_*"), reverse=True)
    for d in fullnode_dirs:
        path = d / "rpc_retained_flow_blocks.csv"
        if path.exists():
            return path
    raise SystemExit("missing full-node RPC flow blocks artifact")


def main() -> int:
    coverage = json.loads((ADDRESS_DIR / "coverage_summary.json").read_text())
    funded_addresses = int(coverage["address_axis"]["address_count"])
    snapshot_height = int(coverage["analysis_window"]["end_height"])

    age_buckets = pd.read_csv(SNAPSHOT_DIR / "utxo_age_buckets.csv")
    utxo_set_btc = float(age_buckets["total_btc"].sum())

    blocks = pd.read_csv(_find_flow_blocks_csv(), low_memory=False)
    transactions = int(blocks["n_tx_noncoinbase"].sum())
    height_lo = int(blocks["height"].min())
    height_hi = int(blocks["height"].max())
    date_lo = str(blocks["date"].min())
    date_hi = str(blocks["date"].max())

    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(15.5, 2.6))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    blocks_spec = [
        (1 / 6, f"{funded_addresses:,}", "Funded addresses",
         f"current balance > 0 · height {snapshot_height:,}", DARK_BLUE),
        (3 / 6, f"{utxo_set_btc:,.0f} BTC", "Current UTXO-set total",
         f"chainstate snapshot · height {snapshot_height:,}", DARK_ORANGE),
        (5 / 6, f"{transactions:,}", "Transactions analyzed",
         f"blocks {height_lo:,}–{height_hi:,} · {date_lo} to {date_hi}", DARK_GRAY),
    ]
    for x, headline, label, detail, color in blocks_spec:
        ax.text(x, 0.62, headline, ha="center", va="center",
                fontsize=33, fontweight="bold", color=color)
        ax.text(x, 0.30, label, ha="center", va="center",
                fontsize=15, color="#111827")
        ax.text(x, 0.10, detail, ha="center", va="center",
                fontsize=11.5, color=LABEL_GRAY)
    for x in (1 / 3, 2 / 3):
        ax.axvline(x, ymin=0.12, ymax=0.88, color=SEPARATOR_GRAY, linewidth=1.2)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig00_dataset_scale.{ext}"
        fig.savefig(out, dpi=170 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
