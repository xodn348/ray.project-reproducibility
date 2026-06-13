# Bitcoin transaction-data paper reproducibility package

This repository reproduces the paper
**“Store of Value, Not Daily Payment: Evidence from Bitcoin Transaction Data.”**

It contains the public summary inputs and scripts needed to rebuild the
manuscript figures and the IEEE-style PDF. Raw Bitcoin node state, the internal
address SQLite database, credentials, and receiver-side shard files are not
included.

## Rebuild

```bash
python3 -m pip install -r requirements.txt
bash scripts/phase2/regen_all.sh
```

Expected result:

- `paper/paper.pdf`
- 10 pages
- 9 active `\includegraphics` figures
- `paper/figures/*.pdf` and `paper/figures/*.png` regenerated from committed summary inputs

The script also mirrors active figures into root `figures/` for upload workflows
and writes optional HoloViz/Bokeh review previews under `paper/figures/holoviz/`.
PNG export for those previews requires local Chrome or Chromium.

## Source map

| Output | Measurement | Source files | Rebuild script |
|---|---|---|---|
| Figure 1 | Macro/protocol timing | `data/events/timeline.csv`, `data/events/regulatory_events.csv` | `scripts/figures/fig01_macro_protocol_timeline.py` |
| Figure 2 | Dataset scale | `data/phase2/address_core_stage1/coverage_summary.json`, `data/phase2/utxo_snapshot_20260523/utxo_age_buckets.csv`, `data/phase2/rpc_retained_flow_fullnode_20260529T193328Z/rpc_retained_flow_blocks.csv` | `scripts/figures/fig00_dataset_scale.py` |
| Figures 3 and 5 | Current UTXO stock and dormancy age | `data/phase2/utxo_snapshot_20260523/manifest.json`, `utxo_age_buckets.csv`, `utxo_cumulative_age.csv` | `scripts/figures/fig02_phase2.py`, `scripts/figures/fig04_phase2.py` |
| Table I and Figure 4 | Full-node block transaction output sums | `data/phase2/rpc_retained_flow_fullnode_20260529T193328Z/manifest.json`, `rpc_retained_flow_summary.csv`, `rpc_retained_flow_blocks.csv`, `rpc_retained_flow_histogram.csv` | `scripts/figures/fig03_phase2.py` |
| Figures 6 and 7 | Script-family UTXO count, BTC balance, and BTC per UTXO | `data/phase2/address_core_stage1/coverage_summary.json`, `script_type_balance.csv` | `scripts/figures/fig05_address_level.py` |
| Table II and Figures 8 and 9 | Address recency, UTXO-count buckets, and top-rank tails | `data/phase2/address_core_stage1/dormancy_balance.csv`, `utxo_count_distribution.csv`, `top_balance.csv`, `top_utxo_count.csv`, `coverage_summary.json` | `scripts/figures/fig05_address_level.py`, `scripts/figures/fig06_address_one_year.py` |

## Data scope

- Chainstate snapshot: Bitcoin Core `dumptxoutset` at height 950,696.
- UTXO snapshot: 165.35M current UTXOs, 20.03M BTC.
- Full-node block window: blocks 684,476 to 950,696, 266,221 contiguous blocks.
- Transaction-flow sample: 718.7M non-coinbase transactions.
- Address-level summary: 56.05M funded address strings and 19.92M address-attributable BTC.
- Address-level source database used to create committed summaries: 707M rows, local-only and not redistributed.

Address strings are transaction-data groups. They are not owner, wallet, or
entity labels. The paper does not use wallet clustering, exchange labels,
owner identification, or change-output correction.
