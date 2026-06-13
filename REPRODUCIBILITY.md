# Reproducibility procedure

1. Install Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. Ensure a LaTeX distribution with `pdflatex` and `bibtex` is available.
3. For optional HoloViz PNG preview export, ensure Chrome or Chromium is available.
4. Rebuild all figures and the manuscript:
   ```bash
   bash scripts/phase2/regen_all.sh
   ```
5. Check the summary printed by the script. The expected manuscript build is
   10 pages and 9 `\includegraphics` entries. A tiny bibliography overfull box
   may appear depending on the local LaTeX line-breaking environment.

## Inputs used by the rebuild

- Figure 1 event sources: `data/events/`.
- Dataset-scale figure: `data/phase2/address_core_stage1/coverage_summary.json`,
  `data/phase2/utxo_snapshot_20260523/utxo_age_buckets.csv`, and
  `data/phase2/rpc_retained_flow_fullnode_20260529T193328Z/rpc_retained_flow_blocks.csv`.
- Stock and dormancy figures: `data/phase2/utxo_snapshot_20260523/`.
- Flow figure and Table I: `data/phase2/rpc_retained_flow_fullnode_20260529T193328Z/`.
- Address-level figures and Table II: `data/phase2/address_core_stage1/`.

Raw block files, node state, credentials, receiver-side shards, and the internal
address SQLite database are intentionally excluded from this public package.
