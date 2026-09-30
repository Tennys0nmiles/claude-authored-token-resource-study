"""Cross-resource 'value atlas' for Pythia-1.4B, from saved per-token results (no model runs).

For the same 108k natural-text tokens (2026 papers + code, positions >= 64) we have the counterfactual value of three
resources:
  memory : a 32-63-token window -> the full 1,024-token context   (gain = nll_window - nll_full)
  depth  : exit after layer 12 (tuned lens) -> all 24 layers      (gain = nll_exit12 - nll_final)
  scale  : Pythia-1.4B -> Pythia-6.9B, both with full context      (gain = nll_1.4B - nll_6.9B)
Question: are the tokens that need one resource the tokens that need another? If not, a single 'difficulty' router
(one gate for all resources, as in adaptive-depth or conditional-attention layers) must misallocate.
Writes analysis/stats/atlas_*.csv."""
import pathlib, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

G = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                 "per_token_results")   # folder holding the per-token parquet files written by the experiments
OUT = pathlib.Path(__file__).resolve().parents[1] / "stats"
a = pd.read_parquet(G / "ladder_pythia-1.4b_to_pythia-6.9b/per_token.parquet")
d = pd.read_parquet(G / "depth_pythia1.4b/per_token_depth.parquet")
assert (a.doc_id.values == d.doc_id.values).all() and (a.pos.values == d.pos.values).all()
df = pd.concat([a, d[["nll_final", "nll_12", "KL_final_12", "H_12"]]], axis=1)


def fam4(g):
    """4-gram ending at t seen earlier, ending at least 64 positions back (outside a 64-token window)."""
    toks = g.tok.values; out = np.zeros(len(toks), bool); seen = {}
    for t in range(len(toks)):
        if t >= 3:
            k = tuple(toks[t - 3:t + 1])
            out[t] = k in seen and seen[k] <= t - 64
            seen.setdefault(k, t)
    return pd.Series(out, index=g.index)


df["fam4"] = df.groupby("doc_id", group_keys=False).apply(fam4)
df = df[(df.pos >= 64) & df.domain.isin(["prose", "code"])].copy()
df["g_mem"] = df.nll_Ss - df.nll_S; df["v_mem"] = df.KL_SSs
df["g_depth"] = df.nll_12 - df.nll_final; df["v_depth"] = df.KL_final_12
df["g_scale"] = df.nll_S - df.nll_L; df["v_scale"] = df.KL_LS
R = ["mem", "depth", "scale"]
NAME = {"mem": "long context", "depth": "upper 12 layers", "scale": "6.9B model"}

rows = []
for i, r1 in enumerate(R):
    for r2 in R[i + 1:]:
        rows.append(dict(a=NAME[r1], b=NAME[r2], rho_value=spearmanr(df[f"v_{r1}"], df[f"v_{r2}"]).statistic,
                         rho_realized=spearmanr(df[f"g_{r1}"], df[f"g_{r2}"]).statistic))
corr = pd.DataFrame(rows)


def recovered(score, gain, b=0.10):
    k = int(round(b * len(score))); sel = np.argsort(-score, kind="stable")[:k]
    return 100 * gain[sel].sum() / gain.sum()


# cross-allocation: give resource X to the top 10% of tokens ranked by some signal; % of X's total gain recovered
signals = {"oracle for long context": df.v_mem.values, "oracle for depth": df.v_depth.values,
           "oracle for 6.9B": df.v_scale.values, "entropy (full context)": df.H_S.values,
           "entropy (window)": df.H_Ss.values, "random": np.random.default_rng(0).random(len(df))}
xa = pd.DataFrame({NAME[r]: {s: recovered(v, df[f"g_{r}"].values) for s, v in signals.items()} for r in R})

# overlap of the top-10% sets under each resource's own oracle
top = {r: set(np.argsort(-df[f"v_{r}"].values, kind="stable")[: int(0.1 * len(df))]) for r in R}
ov = pd.DataFrame([dict(a=NAME[r1], b=NAME[r2], overlap=len(top[r1] & top[r2]) / len(top[r1]))
                   for i, r1 in enumerate(R) for r2 in R[i + 1:]])

# where each resource's value sits: share of total gain on 'familiar' tokens (4-gram seen far back)
famshare = pd.DataFrame([dict(resource=NAME[r], tokens_share=100 * df.fam4.mean(),
                              gain_share=100 * df.loc[df.fam4, f"g_{r}"].sum() / df[f"g_{r}"].sum(),
                              mean_gain_familiar=df.loc[df.fam4, f"g_{r}"].mean(),
                              mean_gain_other=df.loc[~df.fam4, f"g_{r}"].mean()) for r in R])
# best case for one shared ranking: requires all three oracle values (so no practical router can do better)
zsum = sum((df[f"v_{r}"] - df[f"v_{r}"].mean()) / df[f"v_{r}"].std() for r in R).values
shared = pd.DataFrame({"own oracle": {NAME[r]: recovered(df[f"v_{r}"].values, df[f"g_{r}"].values) for r in R},
                       "shared: sum of standardised oracle values": {NAME[r]: recovered(zsum, df[f"g_{r}"].values) for r in R}}).T
shared.to_csv(OUT / "atlas_shared_ranking.csv")
corr.to_csv(OUT / "atlas_correlations.csv", index=False); xa.to_csv(OUT / "atlas_cross_allocation.csv")
ov.to_csv(OUT / "atlas_top10_overlap.csv", index=False); famshare.to_csv(OUT / "atlas_familiar_share.csv", index=False)
pd.set_option("display.width", 200)
print(f"{len(df):,} tokens; mean gains (nats): " + ", ".join(f"{NAME[r]} {df[f'g_{r}'].mean():.3f}" for r in R))
print(corr.round(3).to_string(index=False)); print()
print("top-10% overlap between resources (independence would give 0.10):"); print(ov.round(3).to_string(index=False)); print()
print("% of each resource's total gain recovered by giving it to the top 10% of tokens under each signal:")
print(xa.round(1).to_string()); print()
print(famshare.round(3).to_string(index=False))
