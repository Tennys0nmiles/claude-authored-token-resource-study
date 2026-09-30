#!/bin/bash
# Queue v5 (runs on the pod, /workspace/ml): remaining experiments, one at a time, exit codes logged.
cd /workspace/ml; export HF_HOME=/workspace/hf PYTHONUNBUFFERED=1; L=logs; mkdir -p $L results/e2e_v2
run() { local name=$1; shift; echo "=== $(date -u +%FT%TZ) START $name" >> $L/queue.log
        "$@" > $L/$name.log 2>&1; echo "=== $(date -u +%FT%TZ) END $name rc=$?" >> $L/queue.log; }
until grep -q "PREFETCH DONE" $L/prefetch.log 2>/dev/null; do sleep 10; done
E="python e2e_v2.py"; LONG="--docs data/docs_long.jsonl"
run bench             python attn_bench.py
run q15_4k_w1024_all  $E --model Qwen/Qwen2.5-1.5B --W 1024 --T 4096 $LONG --splits 0 --blocks --conds all
run p14_1k_w256_all   $E --model EleutherAI/pythia-1.4b-deduped --W 256 --splits 0 --blocks --conds all
run atlas_q15_8k      $E --model Qwen/Qwen2.5-1.5B --W 1024 --T 8192 $LONG --pass1-only
run atlas_q7_8k       $E --model Qwen/Qwen2.5-7B --W 1024 --T 8192 $LONG --pass1-only --dtype bf16 --batch 2
run p160_1k_w64_all   $E --model EleutherAI/pythia-160m-deduped --W 64 --splits 0 --blocks --conds all
run p410_1k_w64       $E --model EleutherAI/pythia-410m-deduped --W 64 --splits 0
run p410_1k_w256      $E --model EleutherAI/pythia-410m-deduped --W 256 --splits 0
run p14_1k_w64        $E --model EleutherAI/pythia-1.4b-deduped --W 64 --splits 0
run q15_4k_w256       $E --model Qwen/Qwen2.5-1.5B --W 256 --T 4096 $LONG --splits 0
run q7_8k_w256        $E --model Qwen/Qwen2.5-7B --W 256 --T 8192 $LONG --splits 0 --dtype bf16 --batch 2
echo "=== $(date -u +%FT%TZ) QUEUE V5 DONE" >> $L/queue.log
