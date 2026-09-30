#!/usr/bin/env bash
# Rebuild the paper from the saved results in this repository: statistics -> tables -> figures -> PDFs.
# No model is run.   ./build.sh             full rebuild
#                    ./build.sh --tex-only  compile only
# Needs python3 with numpy, pandas and matplotlib (set PY=/path/to/python), and pdflatex + bibtex.
# Makes two PDFs from one source: main.pdf (arXiv version, human author) and main_jaigp.pdf
# (Journal for AI Generated Papers version: Claude as author, the human as prompter).
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}

if [[ "${1:-}" != "--tex-only" ]]; then
  "$PY" ../analysis/scripts/make_stats_v2.py > /dev/null   # gating, block selection, recurrence (../gpu_results_session3)
  "$PY" scripts/make_tables.py    > /dev/null               # LaTeX rows -> tables/
  "$PY" scripts/make_tables_v2.py > /dev/null
  "$PY" scripts/make_figures.py   > /dev/null               # vector figures -> figures/
fi

mkdir -p build
tex() { local job=$1; shift
        pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build -jobname="$job" "$@" > "build/$job.stdout" \
          || { tail -40 "build/$job.stdout"; exit 1; }; }
tex main main.tex
bibtex build/main > build/bibtex.out || { cat build/bibtex.out; exit 1; }
tex main main.tex; tex main main.tex; tex main main.tex
cp build/main.bbl build/main_jaigp.bbl
for i in 1 2 3; do tex main_jaigp '\def\jaigpbuild{1}\input{main.tex}'; done
cp build/main.pdf build/main_jaigp.pdf .
echo "built main.pdf and main_jaigp.pdf ($(pdfinfo main.pdf | awk '/^Pages/{print $2}') pages each)"
