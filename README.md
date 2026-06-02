# Bitcoin transaction-data paper reproducibility package

This repository reproduces the paper
**“Store of Value, Not Daily Payment: Evidence from Bitcoin Transaction Data.”**

It contains the materials needed to rebuild the manuscript:

- figure-generation code in `scripts/figures/`
- rebuild procedure in `scripts/phase2/regen_all.sh`
- summary source data under `data/`
- LaTeX manuscript source under `paper/`
- figure PDFs/PNGs under `paper/figures/`

## Rebuild

```bash
python3 -m pip install -r requirements.txt
bash scripts/phase2/regen_all.sh
```

Expected result:

- `paper/paper.pdf`
- 10 pages
- 8 active `\includegraphics` figures
- zero final-pass LaTeX/Overfull/Underfull warnings

The rebuild script also writes optional HoloViz/Bokeh review previews under
`paper/figures/holoviz/`. PNG export for those previews requires local Chrome
or Chromium. The canonical manuscript figures are the static PDF/PNG files
under `paper/figures/`.

## Source map

| Output | Source files | Rebuild script |
|---|---|---|
| Figure 1 | `data/events/*.csv`, `data/macro/taproot_adoption_snapshot.csv` | `scripts/figures/fig01_macro_protocol_timeline.py` |
| Figures 2 and 4 | `data/phase2/utxo_snapshot_20260523/*.csv`, `manifest.json` | `fig02_phase2.py`, `fig04_phase2.py` |
| Table I and Figure 3 | `data/phase2/rpc_retained_flow_fullnode_20260529T193328Z/*` | `fig03_phase2.py` |
| Figures 5 and 6 | `data/phase2/address_core_stage1/coverage_summary.json`, `script_type_balance.csv` | `fig05_address_level.py` |
| Table II and Figures 7--8 | address recency, UTXO-count, and top-rank summaries in `data/phase2/address_core_stage1/` | `fig05_address_level.py`, `fig06_address_one_year.py` |
| Paper PDF | `paper/paper.tex`, `paper/references.bib`, `paper/figures/*.pdf` | `scripts/phase2/regen_all.sh` |

## Data sources

The source data are summary products derived from Bitcoin Core chainstate and
full-node block reads. They are sufficient to rebuild the figures and paper.
The package keeps source tables, plotting code, and manuscript files; raw node
state, credentials, and run logs are excluded. Address strings are
transaction-data groups; they are not owner, wallet, or entity labels.
