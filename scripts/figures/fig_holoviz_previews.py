#!/usr/bin/env python3
"""Generate optional HoloViz/Bokeh HTML previews for Fig. 2--4.

Static PDF/PNG figures remain the manuscript source; these HTML previews are
only for visual review.
"""
from __future__ import annotations

import json
from pathlib import Path

import holoviews as hv
import pandas as pd

hv.extension("bokeh")

ROOT = Path(__file__).resolve().parents[2]
PHASE2 = ROOT / "data" / "phase2"
SNAP = PHASE2 / "utxo_snapshot_20260523"
OUT_DIR = ROOT / "paper" / "figures" / "holoviz"
OUT_DIR.mkdir(parents=True, exist_ok=True)
INK = "#0f172a"
BLUE = "#2563eb"
NAVY = "#172554"
TEAL = "#0f766e"
AMBER = "#d97706"
PLUM = "#5b21b6"


def _complete_rpc_dir(d: Path) -> bool:
    required = ["manifest.json", "rpc_retained_flow_summary.csv", "rpc_retained_flow_histogram.csv"]
    if not all((d / name).exists() for name in required):
        return False
    try:
        manifest = json.loads((d / "manifest.json").read_text())
    except Exception:
        return False
    expected = int(manifest.get("end_height", -1)) - int(manifest.get("start_height", 0)) + 1
    return (
        expected > 0
        and int(manifest.get("processed_blocks", -1)) == expected
        and int(manifest.get("skipped_blocks", -1)) == 0
        and not (d / "FAILED_INVALID_OUTPUTS.json").exists()
    )


def _rpc_dir() -> Path:
    for d in sorted(PHASE2.glob("rpc_retained_flow_fullnode_*"), reverse=True):
        if _complete_rpc_dir(d):
            return d
    raise SystemExit("missing completed full-node RPC flow artifact")


def _smooth_density(group: pd.DataFrame) -> pd.DataFrame:
    g = group.sort_values("log10_btc_mid").copy()
    counts = pd.to_numeric(g["tx_count"], errors="coerce").fillna(0.0).astype(float)
    smooth = counts.rolling(window=7, center=True, min_periods=1).mean()
    denom = smooth.sum()
    g["density"] = smooth / denom if denom > 0 else 0.0
    return g


def fig02() -> Path:
    age = pd.read_csv(SNAP / "utxo_age_buckets.csv")
    cum = pd.read_csv(SNAP / "utxo_cumulative_age.csv")
    age["share_pct"] = pd.to_numeric(age["share_of_total_btc"], errors="coerce") * 100
    age["btc_m"] = pd.to_numeric(age["total_btc"], errors="coerce") / 1_000_000
    cum["share_pct"] = pd.to_numeric(cum["share_of_total_btc"], errors="coerce") * 100

    bars = hv.Bars(age, kdims="bucket", vdims=["share_pct", "btc_m"]).opts(
        title="Fig. 2 Stock lens — local UTXO age composition",
        width=980,
        height=430,
        color=BLUE,
        line_color="white",
        tools=["hover"],
        toolbar="disable",
        xlabel="Age bucket",
        ylabel="Share of UTXO-set BTC (%)",
        xrotation=28,
        fontscale=1.18,
    )
    age_labels = hv.Labels(age.assign(label=age["share_pct"].map(lambda v: f"{v:.1f}%")), kdims=["bucket", "share_pct"], vdims="label").opts(text_font_size="9pt", text_color=INK, yoffset=1.0)
    curve = hv.Curve(cum, kdims="threshold", vdims="share_pct").opts(
        width=420,
        height=430,
        color=TEAL,
        line_width=3,
        tools=["hover"],
        xlabel="Threshold",
        ylabel="BTC still unspent (%)",
        xrotation=55,
        ylim=(0, 105),
        fontscale=1.18,
        toolbar="disable",
    ) * hv.Scatter(cum, kdims="threshold", vdims="share_pct").opts(color=TEAL, size=8, tools=["hover"])
    layout = ((bars * age_labels) + curve).opts(shared_axes=False).cols(2)
    out = OUT_DIR / "fig02_stock_lens_holoviz.html"
    hv.save(layout, out)
    return out


def fig03() -> Path:
    rdir = _rpc_dir()
    hist = pd.read_csv(rdir / "rpc_retained_flow_histogram.csv")
    summ = pd.read_csv(rdir / "rpc_retained_flow_summary.csv")
    hist = hist[hist["period_type"].eq("year")].copy()
    summ = summ[summ["period_type"].eq("year")].copy()
    hist["period"] = hist["period"].astype(str)
    summ["period"] = summ["period"].astype(str)
    hist["btc_mid"] = pd.to_numeric(hist["btc_mid"], errors="coerce")
    hist["log10_btc_mid"] = pd.to_numeric(hist["log10_btc_mid"], errors="coerce")
    hist["tx_count"] = pd.to_numeric(hist["tx_count"], errors="coerce").fillna(0)

    overlay = None
    palette = [PLUM, AMBER, "#dc2626", "#0891b2", "#16a34a"]
    for i, year in enumerate(sorted(hist["period"].unique())):
        g = _smooth_density(hist[hist["period"].eq(year)])
        row = summ[summ["period"].eq(year)].iloc[0]
        label = f"{year}: median {float(row['median_btc_approx']):.4g} BTC, p90 {float(row['p90_btc_approx']):.3g}"
        curve = hv.Curve(g, kdims="btc_mid", vdims="density", label=label).opts(
            color=palette[i % len(palette)], line_width=3, tools=["hover"]
        )
        overlay = curve if overlay is None else overlay * curve
    assert overlay is not None
    overlay = overlay.opts(
        title=f"Fig. 3 Flow lens — transaction output distribution ({rdir.relative_to(ROOT)})",
        width=1180,
        height=560,
        logx=True,
        xlabel="Transaction output sum excluding coinbase (BTC, log scale)",
        ylabel="Smoothed transaction-share density per log bin",
        legend_position="top_right",
        fontscale=1.18,
        show_grid=True,
        toolbar="disable",
        xlim=(1e-8, 1e2),
    )
    out = OUT_DIR / "fig03_flow_lens_holoviz.html"
    hv.save(overlay, out)
    return out


def fig04() -> Path:
    cum = pd.read_csv(SNAP / "utxo_cumulative_age.csv")
    cum["share_pct"] = pd.to_numeric(cum["share_of_total_btc"], errors="coerce") * 100
    cuts = cum[cum["threshold"].isin([">=1 year", ">=3 years", ">=5 years"])].copy()
    curve = hv.Curve(cum, kdims="threshold", vdims="share_pct").opts(
        title="Fig. 4 Sink lens — dormant BTC terminal-stock proxy",
        width=880,
        height=430,
        color=TEAL,
        line_width=3,
        tools=["hover"],
        xlabel="Minimum UTXO age threshold",
        ylabel="BTC still unspent (%)",
        xrotation=35,
        ylim=(0, 105),
        fontscale=1.18,
        toolbar="disable",
    ) * hv.Scatter(cum, kdims="threshold", vdims="share_pct").opts(color=TEAL, size=8, tools=["hover"])
    bars = hv.Bars(cuts, kdims="threshold", vdims="share_pct").opts(
        width=430,
        height=430,
        color=NAVY,
        line_color="white",
        tools=["hover"],
        xlabel="Terminal-stock cut",
        ylabel="Share of BTC (%)",
        xrotation=20,
        fontscale=1.18,
        toolbar="disable",
    )
    cut_labels = hv.Labels(cuts.assign(label=cuts["share_pct"].map(lambda v: f"{v:.1f}%")), kdims=["threshold", "share_pct"], vdims="label").opts(text_font_size="10pt", text_color=INK, yoffset=1.2)
    layout = (curve + (bars * cut_labels)).opts(shared_axes=False).cols(2)
    out = OUT_DIR / "fig04_sink_lens_holoviz.html"
    hv.save(layout, out)
    return out


def main() -> int:
    for out in (fig02(), fig03(), fig04()):
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
