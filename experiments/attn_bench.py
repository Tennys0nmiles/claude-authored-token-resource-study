"""Attention-only microbenchmark: one layer, batch 1, bf16, Qwen2.5-7B shapes (28 query heads, 4 KV heads, head dim
128). Full causal attention (FlashAttention via SDPA) vs the gated scheme: sliding-window attention (window W plus
the first token) for every query, plus full-prefix attention for a gathered fraction b of the queries, both with
FlexAttention block masks. Times are medians of CUDA-synchronised repeats. This measures attention kernels only, not
a whole model; see the paper's discussion for what else a deployment needs."""
import json, pathlib, statistics, time
import torch
import torch.nn.functional as F
from torch.nn.attention import SDPBackend, sdpa_kernel
from torch.nn.attention.flex_attention import flex_attention, create_block_mask

torch.manual_seed(0)
dev, H, HKV, D, W = "cuda", 28, 4, 128, 1024
flex = torch.compile(flex_attention)
OUT = pathlib.Path("results/attn_bench.json"); OUT.parent.mkdir(parents=True, exist_ok=True)


def timeit(fn, reps=20, warm=5):
    for _ in range(warm):
        fn()
    torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        a = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - a)
    return 1000 * statistics.median(ts)


def local_mod(b, h, qi, kv):
    return (kv <= qi) & ((qi - kv < W) | (kv == 0))


def gated_forward(q, k, v, bm_local, pos, bm_g):
    o = flex(q, k, v, block_mask=bm_local, enable_gqa=True)
    o[:, :, pos] = flex(q[:, :, pos], k, v, block_mask=bm_g, enable_gqa=True)
    return o


def check(n=2048, frac=0.1):
    """Correctness at small n in fp32: the gated scheme equals SDPA with the explicit mixed mask."""
    q = torch.randn(1, H, n, D, device=dev); k = torch.randn(1, HKV, n, D, device=dev); v = torch.randn_like(k)
    m = int(frac * n) // 128 * 128
    pos = torch.sort(torch.randperm(n - W, device=dev)[:m] + W).values
    bm_local = create_block_mask(local_mod, None, None, n, n, device=dev)
    bm_g = create_block_mask(lambda b, h, qi, kv: kv <= pos[qi], None, None, m, n, device=dev)
    got = gated_forward(q, k, v, bm_local, pos, bm_g)
    i = torch.arange(n, device=dev)[:, None]; j = torch.arange(n, device=dev)[None, :]
    mask = (j <= i) & ((i - j < W) | (j == 0))
    mask[pos] = (j <= i)[pos]
    ref = F.scaled_dot_product_attention(q, k.repeat_interleave(H // HKV, 1), v.repeat_interleave(H // HKV, 1),
                                         attn_mask=mask)
    return float((got - ref).abs().max())


res = {"check_max_abs_diff_fp32": check(), "rows": []}
print("correctness check, max |diff| =", res["check_max_abs_diff_fp32"], flush=True)
for n in (8192, 16384, 32768, 65536):
    q = torch.randn(1, H, n, D, device=dev, dtype=torch.bfloat16)
    k = torch.randn(1, HKV, n, D, device=dev, dtype=torch.bfloat16); v = torch.randn_like(k)
    kr, vr = k.repeat_interleave(H // HKV, 1), v.repeat_interleave(H // HKV, 1)

    def full():
        with sdpa_kernel(SDPBackend.FLASH_ATTENTION):
            return F.scaled_dot_product_attention(q, kr, vr, is_causal=True)
    bm_local = create_block_mask(local_mod, None, None, n, n, device=dev)
    t_full = timeit(full)
    t_local = timeit(lambda: flex(q, k, v, block_mask=bm_local, enable_gqa=True))
    for frac in (0.05, 0.10, 0.20):
        m = int(frac * n) // 128 * 128
        pos = torch.sort(torch.randperm(n - W, device=dev)[:m] + W).values
        bm_g = create_block_mask(lambda b, h, qi, kv: kv <= pos[qi], None, None, m, n, device=dev)
        t_g = timeit(lambda: gated_forward(q, k, v, bm_local, pos, bm_g))
        row = dict(n=n, W=W, frac=frac, full_flash_ms=t_full, local_only_ms=t_local, gated_ms=t_g,
                   speedup=t_full / t_g)
        res["rows"].append(row); print(json.dumps(row), flush=True)
    del q, k, v, kr, vr
    torch.cuda.empty_cache()
res["torch"] = torch.__version__; res["gpu"] = torch.cuda.get_device_name()
json.dump(res, open(OUT, "w"), indent=1)
