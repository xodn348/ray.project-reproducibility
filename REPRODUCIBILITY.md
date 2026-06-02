# Reproducibility procedure

1. Install Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. Ensure a LaTeX distribution with `pdflatex` and `bibtex` is available.
3. For optional HoloViz PNG preview export, ensure Chrome or Chromium is
   available.
4. Rebuild all figures and the manuscript:
   ```bash
   bash scripts/phase2/regen_all.sh
   ```
5. Check the summary printed by the script. The expected manuscript build is
   10 pages, 8 `\includegraphics` entries, and zero final-pass warnings.

The flow lens is rebuilt from
`data/phase2/rpc_retained_flow_fullnode_20260529T193328Z/`. Address-level
figures and Table II are rebuilt from `data/phase2/address_core_stage1/`.
Raw block files and run logs are not required for this package.
