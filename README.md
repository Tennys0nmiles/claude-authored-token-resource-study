# Different Tokens Need Different Resources: code and results

> **This is AI-conducted research.** Claude (Anthropic's Claude Opus 5.5, working through the Claude Code agent) proposed the hypotheses, designed, implemented and ran every experiment, analysed the results and wrote the paper. The repository owner started the project, paid for the compute, gave high-level direction and reviewed the work, and takes responsibility for its content.

This repository holds the code and results behind the paper *"Different Tokens Need Different Resources: What Predicts the Value of Context, Depth and Scale in Language Models"* (arXiv link to be added).

**Question.** For each token of text written after the models' training data, how much does its loss fall with (a) long context, (b) extra depth, (c) a larger model? Are these the same tokens, and what predicts each?

**Main findings.**
- The tokens that benefit from each resource are largely different tokens.
- Next-token entropy is a partial signal; small linear "value heads" trained on counterfactual outcomes beat it, most strongly for long context.
- The value of long context concentrates on exact recurrence, which a hashed n-gram lookup both detects and locates in the cache.
- For attention over a GPU-resident cache, choosing keys (block selection) beats choosing tokens (per-token gating).

Models: Pythia (160M–6.9B) and Qwen2.5 (1.5B, 7B), frozen, at up to 8k tokens.

## Layout

| Path | Contents |
|---|---|
| `experiments/` | Experiment code (runs the models). |
| `experiments/data/manifest_*.jsonl` | IDs of the evaluation documents: September 2026 arXiv papers and recent Python source files. The texts themselves are not redistributed; the `fetch_*.py` scripts re-download them. |
| `experiments/results/` | Signal-level results (budget curves, selections, transfer). |
| `gpu_results_session1/` | Compute ladder, early-exit depth, and first end-to-end gating runs. |
| `gpu_results_session3/` | Final end-to-end runs: per-token gating, block selection, recurrence addressing (per-document CSVs), plus the kernel benchmark. |
| `analysis/scripts/` | Statistics (document-bootstrap intervals, paired comparisons, cross-resource overlap) computed from the saved results. No model is run. |
| `analysis/stats/` | Outputs of the analysis scripts; every number in the paper comes from these or the result files. |

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
