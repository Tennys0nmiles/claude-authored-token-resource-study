"""Cross-resource atlas at 8k tokens for Qwen2.5 (from e2e_v3.py --pass1-only outputs; no model runs).
Same tokens, same tokenizer, window W=1024 vs the full 8k context:
  memory (1.5B) : nll_window - nll_full for Qwen2.5-1.5B
  memory (7B)   : the same for Qwen2.5-7B
  scale         : Qwen2.5-1.5B -> Qwen2.5-7B, both with full context
Oracles here rank by realized gain (no smooth target exists for scale across two separate runs).
Writes analysis/stats/atlas_qwen_*.csv."""
import glob, pathlib, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

IN = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2] / "gpu_results_session3"
OUT = pathlib.Path(__file__).resolve().parents[1] / "stats"
f15 = glob.glob(str(IN / "**" / "tokens_Qwen2.5-1.5B_T8192_W1024.parquet"), recursive=True)[0]
f7 = glob.glob(str(IN / "**" / "tokens_Qwen2.5-7B_T8192_W1024.parquet"), recursive=True)[0]
a, b = pd.read_parquet(f15), pd.read_parquet(f7)
m = a.merge(b, on=["doc", "pos"], suffixes=("_s", "_l"))
assert (m.tok_s == m.tok_l).all()
m = m[m.domain_s.isin(["prose", "code"]) & (m.pos > 1024)].copy()
m["g_mem_s"] = m.nllA_s - m.nllF_s; m["g_mem_l"] = m.nllA_l - m.nllF_l; m["g_scale"] = m.nllF_s - m.nllF_l
G = {"g_mem_s": "long context (1.5B)", "g_mem_l": "long context (7B)", "g_scale": "7B instead of 1.5B"}
k = int(round(0.1 * len(m)))
top = {g: set(np.argsort(-m[g].values, kind="stable")[:k]) for g in G}
rows = [dict(a=G[x], b=G[y], rho=spearmanr(m[x], m[y]).statistic, top10_overlap=len(top[x] & top[y]) / k)
        for i, x in enumerate(G) for y in list(G)[i + 1:]]
sig = {"oracle: " + v: m[g].values for g, v in G.items()}
sig.update({"entropy of the windowed 1.5B pass": m.HA_s.values, "random": np.random.default_rng(0).random(len(m))})
rec = lambda s, g: 100 * g[np.argsort(-s, kind="stable")[:k]].sum() / g.sum()
xa = pd.DataFrame({v: {s: rec(vals, m[g].values) for s, vals in sig.items()} for g, v in G.items()})
fam = pd.DataFrame([dict(resource=v, tokens_share=100 * m.fam4_s.mean(),
                         gain_share=100 * m.loc[m.fam4_s, g].sum() / m[g].sum()) for g, v in G.items()])
pd.DataFrame(rows).to_csv(OUT / "atlas_qwen_overlap.csv", index=False); xa.to_csv(OUT / "atlas_qwen_cross_allocation.csv")
fam.to_csv(OUT / "atlas_qwen_familiar_share.csv", index=False)
pd.set_option("display.width", 200)
print(f"{len(m):,} tokens (positions > 1024); mean gains: " + ", ".join(f"{v} {m[g].mean():.3f}" for g, v in G.items()))
print(pd.DataFrame(rows).round(3).to_string(index=False)); print(); print(xa.round(1).to_string()); print(); print(fam.round(2).to_string(index=False))
