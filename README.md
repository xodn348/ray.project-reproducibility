# Bitcoin transaction-data paper reproducibility package

This is the clean reproducibility package for the paper
**“Store of Value, Not Daily Payment: Evidence from Bitcoin Transaction Data.”**

It contains only the items needed to reproduce the manuscript figures and PDF:

- figure-generation code in `scripts/figures/`
- the rebuild script `scripts/phase2/regen_all.sh`
- committed summary/source data under `data/`
- LaTeX manuscript source under `paper/`
- pre-rendered figure PDFs/PNGs under `paper/figures/`

The full working repository, raw Bitcoin Core snapshots, intermediate shards,
`.omx` state, and internal run logs are intentionally excluded.

## Rebuild

```bash
python3 -m pip install -r requirements.txt
bash scripts/phase2/regen_all.sh
```

Expected result:

- `paper/paper.pdf`
- 10 pages
- 9 active `\includegraphics` figures
- zero final-pass LaTeX/Overfull/Underfull warnings

## Source map

| Output | Source files | Rebuild script |
|---|---|---|
| Figure 1 | `data/events/*.csv`, `data/macro/taproot_adoption_snapshot.csv` | `scripts/figures/fig01_macro_protocol_timeline.py` |
| Figures 2 and 4 | `data/phase2/utxo_snapshot_20260523/*.csv`, `manifest.json` | `fig02_phase2.py`, `fig04_phase2.py` |
| Table I and Figure 3 | `data/phase2/rpc_retained_flow_20260523/*` | `fig03_phase2.py` |
| Figures 5 and 6 | `data/phase2/address_core_stage1/coverage_summary.json`, `script_type_balance.csv` | `fig05_address_level.py` |
| Table II and Figures 7--9 | address recency, UTXO-count, and top-rank summaries in `data/phase2/address_core_stage1/` | `fig05_address_level.py`, `fig06_address_one_year.py`, `fig07_address_rank_profiles.py` |
| Paper PDF | `paper/paper.tex`, `paper/references.bib`, `paper/figures/*.pdf` | `scripts/phase2/regen_all.sh` |

## Data boundary

The committed data are summary products derived from Bitcoin Core chainstate and
block reads. Raw full-node files and intermediate receiver/address shards are not
included because they are large and not required to rebuild the submitted paper.
