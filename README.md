# Choosing Keys, Not Tokens: code and results

> **This is AI-conducted research.** Claude (Anthropic's Claude Opus 5.5, working through the Claude Code agent) proposed the hypotheses, designed, implemented and ran every experiment, analysed the results and wrote the paper. The repository owner started the project, paid for the compute, gave high-level direction and reviewed the work, and takes responsibility for its content.

This repository holds the code, results and LaTeX source behind the paper *"Choosing Keys, Not Tokens: What Predicts When and Where Far Context Helps"* (Journal for AI Generated Papers; link to be added). An earlier version of the paper was titled *"Different Tokens Need Different Resources"*.

**Read the paper:** [`paper/main_jaigp.pdf`](paper/main_jaigp.pdf). Claude (Anthropic) is the author; Tennyson Miles is the human prompter.

**Question.** For each token of text written after the models' training data, when does attending to far context help, and where in the context does the help come from?

**Main findings.**
- *Motivation:* the tokens that benefit from far context are largely different from those that benefit from extra depth or a larger model. They are largely shared between a 1.5B and a 7B model, and they concentrate on recurrence.
- *Entropy is a poor trigger for far context.* A small linear value head with n-gram familiarity features does 1.6–2.1× better in real masked forward passes (at a 10% budget, nine configurations up to Qwen2.5-7B at 8k tokens).
- *Choose keys, not tokens.* At an equal far-key budget, Quest-style block selection for every query beats per-token gating. At 4k and 8k tokens it beats even an oracle gate.
- *Familiarity says where to look.* Fetching the key blocks that followed earlier occurrences of the current n-gram recovers 28–37% of the benefit while reading 0.6–2.1% of far keys, without scoring any.

Models: Pythia (160M–6.9B) and Qwen2.5 (1.5B, 7B), frozen, at up to 8k tokens.

## Layout

| Path | Contents |
|---|---|
| `experiments/` | Experiment code (runs the models). |
| `experiments/data/manifest_*.jsonl` | IDs of the evaluation documents: September 2026 arXiv papers and recent Python source files. The texts themselves are not redistributed; the `fetch_*.py` scripts re-download them. |
| `experiments/results/` | Signal-level results (budget curves, selections, transfer). |
| `gpu_results_session1/` | Compute ladder, early-exit depth, and first end-to-end gating runs. |
| `gpu_results_session3/` | Final end-to-end runs: per-token gating, block selection, recurrence addressing (per-document CSVs). Also a one-layer kernel benchmark, which was measured but is not reported in the final paper. |
| `analysis/scripts/` | Statistics (document-bootstrap intervals, paired comparisons, cross-resource overlap) computed from the saved results. No model is run. |
| `analysis/stats/` | Outputs of the analysis scripts; every number in the paper comes from these or the result files. Bootstrap seeds are fixed, so the scripts reproduce these files exactly. |
| `paper/` | LaTeX source of the paper, the scripts that write every table and figure (`paper/scripts/`), and `paper/build.sh`. It builds two PDFs from one source: `main_jaigp.pdf` (Claude as author, the human as prompter) and `main.pdf` (arXiv layout, human author). |

## Experiments

| Script | What it measures |
|---|---|
| `fetch_data.py`, `fetch_long.py`, `fetch_lens_data.py` | Download the evaluation texts (1k and full-length) and the disjoint tuned-lens training texts. |
| `collect.py [LARGE_MODEL]` | Per-token losses and features for a small/large Pythia pair (compute) and windowed vs full context (memory). |
| `collect_short.py` | Hidden-state features of the small model on its local window. |
| `analyze.py`, `familiarity.py` | Signal-level budget curves: entropy, value heads, raw-surprise control, familiarity features, oracle. |
| `depth_lens.py` | Tuned-lens early exits in Pythia and the value of the remaining layers. |
| `e2e_gating.py MODEL W` | First end-to-end per-token gating runs (`gpu_results_session1/`). |
| `e2e_v2.py` | Final end-to-end runs: per-token gating in real masked forward passes, Quest-style and exact block selection, recurrence addressing, per-token values for the Qwen atlas (`gpu_results_session3/`). |
| `attn_bench.py` | One-layer attention kernel timing (FlashAttention vs FlexAttention local + gathered full-prefix). |
| `run_gpu_queue.sh` | The exact queue of `e2e_v2.py` / `attn_bench.py` commands used for the final GPU runs. |

Examples:

```bash
pip install -r experiments/requirements.txt    # use a CUDA build of torch for the GPU runs
cd experiments
python fetch_data.py && python fetch_long.py && python fetch_lens_data.py
python collect.py EleutherAI/pythia-1.4b-deduped && python collect_short.py
python analyze.py && python familiarity.py
python e2e_v2.py --model EleutherAI/pythia-160m-deduped --W 64 --T 1024 --splits 0,1,2,3,4
python e2e_v2.py --model Qwen/Qwen2.5-7B --W 1024 --T 8192 --docs data/docs_long.jsonl --splits 0 --dtype bf16 --blocks
```

The fetch scripts take the code-domain files from the installed versions of the packages listed in the manifest, so exact file contents depend on the package versions (see the paper's appendix). arXiv listings change over time; the manifests record which papers were used.

## Rebuilding the paper

```bash
cd paper && ./build.sh    # statistics -> tables -> figures -> both PDFs; needs numpy, pandas, matplotlib, pdflatex, bibtex
```

No model is run: everything comes from the saved results in this repository.

## Analysis

```bash
python analysis/scripts/make_stats_v2.py    # gating, block selection, recurrence, kernel timing (from gpu_results_session3/)
python analysis/scripts/make_stats.py       # first-run statistics (needs experiments/results/per_token.parquet from collect.py)
python analysis/scripts/atlas_qwen.py       # Qwen2.5 cross-resource atlas (needs tokens_*.parquet from e2e_v2.py --pass1-only)
python analysis/scripts/atlas.py DIR        # Pythia three-resource atlas (needs the per-token parquet files from collect.py and depth_lens.py)
```

Per-token parquet files are not included because they contain token IDs of the source texts. They are regenerated by the experiment scripts.

## Compute

All experiments ran on single rented GPUs (RTX PRO 5000, A100 80GB, H100 NVL). Total rental cost was about US$24.

## License

Code: MIT (see `LICENSE`).
