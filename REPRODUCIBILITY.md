# Reproducibility procedure

1. Install Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. Ensure a LaTeX distribution with `pdflatex` and `bibtex` is available.
3. Rebuild all figures and the manuscript:
   ```bash
   bash scripts/phase2/regen_all.sh
   ```
4. Check the summary printed by the script. The expected manuscript build is
   10 pages, 8 `\includegraphics` entries, and zero final-pass warnings.
