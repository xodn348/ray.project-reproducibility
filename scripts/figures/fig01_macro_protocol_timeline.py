# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportUnhashable=false, reportOperatorIssue=false
"""Hand-curated macro/protocol event timeline."""
from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

START = pd.Timestamp("2021-05-22")
END = pd.Timestamp("2026-05-23")

PHASES = [
    ("2021-05-22", "2022-03-15", "Retail\nrisk peak", "#fde8d7"),
    ("2022-03-16", "2023-03-09", "Tightening\n+ FTX", "#f7c6b8"),
    ("2023-03-10", "2024-01-09", "Bank stress /\nETF run up", "#e7d8f0"),
    ("2024-01-10", "2024-09-17", "ETF + halving\n+ Mt.Gox", "#cfe6cf"),
    ("2024-09-18", "2026-05-23", "Institutional\ncustody regime", "#cfe1f2"),
]

MACRO_EVENTS = [
    ("2022-03-16", "Fed hiking\ncycle starts", 0, 0.80),
    ("2022-11-08", "FTX\ncollapse", -28, 0.22),
    ("2023-03-12", "SVB / BTFP", 22, 0.80),
    ("2023-08-29", "Grayscale\nv. SEC", 20, 0.22),
    ("2024-01-10", "Spot ETF\napproval", -36, 0.80),
    ("2024-04-19", "4th\nhalving", 28, 0.22),
    ("2024-07-05", "Mt.Gox\ndistributions", 46, 0.80),
    ("2024-09-18", "First Fed\ncut", 24, 0.22),
]

PROTOCOL_EVENTS = [
    ("2021-11-14", "Taproot", 0, 0.80),
    ("2023-01-21", "Ordinals", -45, 0.22),
    ("2023-03-08", "BRC-20", 50, 0.80),
    ("2023-09-12", "Core 26\nBIP324 test", -20, 0.22),
    ("2024-04-19", "Runes", 42, 0.80),
    ("2024-11-15", "P2QRH\ndraft", -24, 0.22),
]


def add_phase_background(ax: Axes, alpha: float) -> None:
    for start_s, end_s, _label, color in PHASES:
        ax.axvspan(pd.Timestamp(start_s), pd.Timestamp(end_s), color=color, alpha=alpha, zorder=0)


def setup_timeline_axis(ax: Axes) -> None:
    ax.set_xlim(START, END)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.axhline(0.5, color="#9ca3af", linewidth=1.0, zorder=1)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator((1, 4, 7, 10)))
    for spine in ("left", "right", "top"):
        ax.spines[spine].set_visible(False)


def add_timeline(ax: Axes, events: list[tuple[str, str, int, float]], color: str) -> None:
    for date_s, label, x_offset_days, y in events:
        d = pd.Timestamp(date_s)
        text_d = d + pd.Timedelta(days=x_offset_days)
        ax.plot(
            [d],
            [0.5],
            marker="o",
            markersize=9.5,
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=1.35,
            zorder=4,
        )
        ax.annotate(
            label,
            xy=(d, 0.5),
            xytext=(text_d, y),
            ha="center",
            va="center",
            fontsize=13,
            linespacing=0.95,
            arrowprops=dict(arrowstyle="-", color=color, linewidth=0.9, alpha=0.72),
            bbox=dict(boxstyle="round,pad=0.24", fc="white", ec="#777", lw=0.55, alpha=0.96),
        )


def add_phase_band(ax: Axes) -> None:
    ax.set_xlim(START, END)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    for spine in ("left", "right", "top", "bottom"):
        ax.spines[spine].set_visible(False)
    for start_s, end_s, label, color in PHASES:
        start = pd.Timestamp(start_s)
        end = pd.Timestamp(end_s)
        ax.axvspan(start, end, color=color, alpha=0.78, zorder=0)
        mid = start + (end - start) / 2
        ax.text(
            mid,
            0.5,
            label,
            ha="center",
            va="center",
            fontsize=11.3,
            fontweight="semibold",
            color="#333",
            linespacing=0.92,
        )
    ax.text(
        START - pd.Timedelta(days=42),
        0.5,
        "regime\nbands",
        ha="right",
        va="center",
        fontsize=10.8,
        color="#555",
        linespacing=0.92,
        clip_on=False,
    )


def main() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.titlesize": 18,
        "axes.labelsize": 15,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
    })

    fig = plt.figure(figsize=(11.2, 4.95))
    # Fixed axes positions avoid the title/tick/label collisions that appear
    # when tight_layout tries to infer space from many annotation boxes.
    ax0 = fig.add_axes([0.075, 0.865, 0.90, 0.095])
    ax1 = fig.add_axes([0.075, 0.545, 0.90, 0.245])
    ax2 = fig.add_axes([0.075, 0.205, 0.90, 0.245], sharex=ax1)

    add_phase_band(ax0)
    for ax in (ax1, ax2):
        add_phase_background(ax, alpha=0.46)
        setup_timeline_axis(ax)

    add_timeline(ax1, MACRO_EVENTS, "#334155")
    add_timeline(ax2, PROTOCOL_EVENTS, "#0e7c66")

    ax1.tick_params(axis="x", which="both", labelbottom=False)
    ax2.set_xlabel("Event chronology", labelpad=8)
    fig.text(0.525, 0.815, "Macro, regulatory, and custody forcing events", ha="center", va="center", fontsize=18)
    fig.text(0.525, 0.475, "Protocol and blockspace events", ha="center", va="center", fontsize=18)

    for ext in ("png", "pdf"):
        out = OUT_DIR / f"fig01_macro_protocol_timeline.{ext}"
        fig.savefig(out, dpi=170 if ext == "png" else None, bbox_inches="tight")
        print(f"wrote {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
