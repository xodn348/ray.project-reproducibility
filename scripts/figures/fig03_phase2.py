# pyright: reportCallIssue=false
"""Full-node block transaction output time-series figure."""
from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PHASE2_DIR = ROOT / "data" / "phase2"
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)



def _find_rpc_dir() -> Path | None:
    fullnode_dirs = sorted(PHASE2_DIR.glob("rpc_retained_flow_fullnode_*"), reverse=True)
    for d in fullnode_dirs:
        if (d / "manifest.json").exists() and (d / "rpc_retained_flow_summary.csv").exists():
            return d
    return None


def render_rpc_figure(rpc_dir: Path) -> None:
    summary = pd.read_csv(rpc_dir / "rpc_retained_flow_summary.csv")
    month_summary = summary[summary["period_type"] == "month"].copy()
    month_summary["month"] = pd.to_datetime(month_summary["period"] + "-01")
    month_summary = month_summary.sort_values("month")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 18,
        "axes.labelsize": 15,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "legend.fontsize": 12,
    })

    fig, ax = plt.subplots(figsize=(14.2, 6.6))
    x = month_summary["month"]
    ax.plot(x, month_summary["median_btc_approx"], marker="o", linewidth=2.6,
            color="#2563eb", label="median")
    ax.plot(x, month_summary["p90_btc_approx"], marker="s", linewidth=2.6,
            color="#059669", label="p90")
    ax.plot(x, month_summary["p99_btc_approx"], marker="^", linewidth=2.8,
            color="#7c2d12", label="p99")
    ax.fill_between(
        x,
        month_summary["median_btc_approx"],
        month_summary["p99_btc_approx"],
        color="#f59e0b",
        alpha=0.12,
        linewidth=0,
    )

    ax.set_yscale("log")
    ax.set_ylim(2e-4, 60)
    ax.set_xlabel("Month")
    ax.set_ylabel("Transaction output sum, BTC")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.grid(True, axis="both", which="major", linestyle=":", linewidth=0.7, alpha=0.48)
    ax.legend(loc="upper right", frameon=True, framealpha=0.92)
    fig.autofmt_xdate(rotation=0, ha="center")

    fig.suptitle("Monthly transaction output sums in full-node blocks", fontsize=18, y=1.0)
    out_png = OUT_DIR / "fig03_flow_lens_kde.png"
    out_pdf = OUT_DIR / "fig03_flow_lens_kde.pdf"
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig03-phase2] rendered full-node block figure from {rpc_dir.relative_to(ROOT)}")
    print(f"wrote {out_png}")
    print(f"wrote {out_pdf}")


def main() -> int:
    rpc_dir = _find_rpc_dir()
    if rpc_dir is not None:
        render_rpc_figure(rpc_dir)
        return 0

    raise SystemExit("missing full-node RPC flow artifact")


if __name__ == "__main__":
    raise SystemExit(main())
