#!/usr/bin/env bash
# Phase 2 full pipeline: regenerate figures and rebuild PDF.
#
# Run from any directory; resolves to repo root via this script's path.
#
# Steps:
#   1. regenerate all active in-body figures, with Phase 2 wrappers for Fig 2--4
#   2. Mirror paper/figures into root figures/ for Overleaf folder uploads
#   3. pdflatex x2           — rebuild paper/paper.pdf (twice for cross-refs)
#   4. summary               — page count, figure count, warning count

set -u

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$ROOT"

echo "[regen] root: $ROOT"

echo "[regen] step 1: regenerate the active figures"
mkdir -p "$ROOT/paper/figures" "$ROOT/figures"
find "$ROOT/paper/figures" -maxdepth 1 -type f \( -name '*.pdf' -o -name '*.png' \) -delete
find "$ROOT/figures" -maxdepth 1 -type f \( -name '*.pdf' -o -name '*.png' \) -delete
for f in \
    fig01_macro_protocol_timeline.py \
    fig02_phase2.py \
    fig03_phase2.py \
    fig04_phase2.py \
    fig05_address_level.py \
    fig06_address_one_year.py
do
    echo "[regen]   running scripts/figures/$f"
    python "scripts/figures/$f" || {
        echo "[regen] ERROR: scripts/figures/$f failed"
        exit 1
    }
done

echo "[regen] step 2: mirror active paper/figures into root figures/ for Overleaf"
for ext in pdf png; do
    for stem in \
        fig01_macro_protocol_timeline \
        fig02_stock_lens \
        fig03_flow_lens_kde \
        fig04_sink_lens \
        fig05_script_family_mix \
        fig06_script_value_per_utxo \
        fig05_address_count_rank \
        fig06_address_one_year
    do
        src="$ROOT/paper/figures/${stem}.${ext}"
        [ -e "$src" ] || { echo "[regen] ERROR: missing $src"; exit 1; }
        cp "$src" "$ROOT/figures/"
    done
done

echo "[regen] step 3: compile paper.pdf (pdflatex + bibtex + pdflatex x2)"
cd "$ROOT/paper"
# Class/style changes can leave stale aux commands (for example elsarticle
# frontmatter macros) that break the next IEEEtran build, so clean generated
# TeX state before the first pass.
rm -f paper.aux paper.bbl paper.blg paper.out paper.toc paper.spl paper.synctex.gz
LOG_FILE="$(mktemp)"
pdflatex -interaction=nonstopmode paper.tex > "$LOG_FILE" 2>&1 || {
    echo "[regen] ERROR: first pdflatex pass failed; tail of log:"
    tail -40 "$LOG_FILE"
    exit 1
}
bibtex paper > "$LOG_FILE.bib" 2>&1 || true   # bibtex may warn; do not abort
pdflatex -interaction=nonstopmode paper.tex > "$LOG_FILE" 2>&1 || {
    echo "[regen] ERROR: second pdflatex pass failed; tail of log:"
    tail -40 "$LOG_FILE"
    exit 1
}
pdflatex -interaction=nonstopmode paper.tex > "$LOG_FILE" 2>&1 || {
    echo "[regen] ERROR: third pdflatex pass failed; tail of log:"
    tail -40 "$LOG_FILE"
    exit 1
}

echo "[regen] step 4: summary"
if command -v pdfinfo >/dev/null 2>&1; then
    PAGES=$(pdfinfo paper.pdf | awk '/^Pages:/ {print $2}')
else
    # Fallback: grep \pageref from .log
    PAGES=$(grep -c "^! " "$LOG_FILE" >/dev/null; echo "?")
fi
FIG_COUNT=$(grep -c "\\\\includegraphics" paper.tex)
WARN_COUNT=$(grep -cE "(LaTeX Warning|Overfull|Underfull)" "$LOG_FILE" || true)
echo "[regen]   pages   : $PAGES"
echo "[regen]   figures : $FIG_COUNT (\\includegraphics count)"
echo "[regen]   warnings: $WARN_COUNT (LaTeX/Overfull/Underfull)"
echo "[regen] done"
rm -f "$LOG_FILE" "$LOG_FILE.bib"
