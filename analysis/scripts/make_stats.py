"""Statistics for the paper, computed from saved per-document / per-token results (no model runs).

- Document-level bootstrap (2000 resamples) 95% CIs for end-to-end gating results at a 10% budget,
  including the paired difference (learned head - entropy) on the same documents.
- Entropy-decile table for the signal-level pilot (memory gain vs short-window entropy;
  compute gain vs full-context entropy).
Outputs: analysis/stats/*.csv, *.json
"""
import glob, json, os, pathlib
import numpy as np
import pandas as pd

ML = pathlib.Path(__file__).resolve().parents[2]
OUT = ML / "analysis" / "stats"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(0)
B = 2000

POL = {"entropy (local pass)": "entropy",
       "familiarity rule (no training)": "fam_rule",
       "familiarity head (7 scalars)": "fam_head",
       "learned head (hidden only, ablation)": "hidden_only",
       "learned head (hidden + familiarity)": "learned",
       "oracle KL (needs full pass)": "oracle",
       "random": "random"}


def recovered(df):
    return 100 * (df.nllA - df.nllG).sum() / (df.nllA - df.nllF).sum()


def e2e_stats(path, pool):
    R = pd.read_csv(path)
    R = R[R.domain.isin(["prose", "code"])] if pool == "natural" else R[R.domain == pool]   # pools: natural, prose, code, prose_ids
    out = {}
    docs = R.doc.unique()
    idx = {p: {b: g.set_index("doc") for b, g in gp.groupby("budget")} for p, gp in R.groupby("policy")}
    boots = rng.integers(0, len(docs), size=(B, len(docs)))
    for pol, short in POL.items():
        if pol not in idx:
            continue
        for b in (0.05, 0.1, 0.2, 0.3):
            g = idx[pol][b].loc[docs]
            num = (g.nllA - g.nllG).values; den = (g.nllA - g.nllF).values
            point = 100 * num.sum() / den.sum()
            bs = 100 * num[boots].sum(1) / den[boots].sum(1)
            out[(short, b)] = dict(point=point, lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5), boot=bs)
    # paired differences / ratios vs entropy at 10%
    pairs = {}
    for short in ("fam_rule", "fam_head", "hidden_only", "learned"):
        if (short, 0.1) in out:
            d = out[(short, 0.1)]["boot"] - out[("entropy", 0.1)]["boot"]
            r = out[(short, 0.1)]["boot"] / out[("entropy", 0.1)]["boot"]
            pairs[short] = dict(diff=out[(short, 0.1)]["point"] - out[("entropy", 0.1)]["point"],
                                diff_lo=np.percentile(d, 2.5), diff_hi=np.percentile(d, 97.5),
                                ratio=out[(short, 0.1)]["point"] / out[("entropy", 0.1)]["point"],
                                ratio_lo=np.percentile(r, 2.5), ratio_hi=np.percentile(r, 97.5))
    if ("learned", 0.1) in out and ("hidden_only", 0.1) in out:
        d = out[("learned", 0.1)]["boot"] - out[("hidden_only", 0.1)]["boot"]
        pairs["familiarity_contribution"] = dict(diff=out[("learned", 0.1)]["point"] - out[("hidden_only", 0.1)]["point"],
                                                 diff_lo=np.percentile(d, 2.5), diff_hi=np.percentile(d, 97.5))
    return out, pairs, len(docs)


rows, prow = [], []
res1 = ML / "gpu_results_session1"
configs = {
    "Pythia-160M, 1k, W=64": res1 / "e2e/e2e_pythia-160m-deduped_W64.csv",
    "Pythia-410M, 1k, W=64": res1 / "e2e/e2e_pythia-410m-deduped_W64.csv",
    "Pythia-410M, 1k, W=256": res1 / "e2e_ablation/e2e_pythia-410m-deduped_W256.csv",
    "Pythia-1.4B, 1k, W=64": res1 / "e2e/e2e_pythia-1.4b-deduped_W64.csv",
    "Pythia-1.4B, 1k, W=256": res1 / "e2e_ablation/e2e_pythia-1.4b-deduped_W256.csv",
    "Qwen2.5-1.5B, 4k, W=256": res1 / "e2e_long/e2e_Qwen2.5-1.5B_W256.csv",
    "Qwen2.5-1.5B, 4k, W=1024": res1 / "e2e_ablation/e2e_Qwen2.5-1.5B_W1024.csv",
}
for name, path in configs.items():
    for pool in ("natural", "prose", "code", "prose_ids"):
        out, pairs, nd = e2e_stats(path, pool)
        for (short, b), v in out.items():
            rows.append(dict(config=name, pool=pool, n_docs=nd, policy=short, budget=b,
                             point=round(v["point"], 6), lo=round(v["lo"], 6), hi=round(v["hi"], 6)))
        for short, v in pairs.items():
            prow.append(dict(config=name, pool=pool, comparison=short, **{k: round(x, 6) for k, x in v.items()}))
pd.DataFrame(rows).to_csv(OUT / "e2e_bootstrap.csv", index=False)
pd.DataFrame(prow).to_csv(OUT / "e2e_paired.csv", index=False)

# ---- entropy deciles from the pilot (signal level)
pt = pd.read_parquet(ML / "experiments/results/per_token.parquet")
pt = pt[(pt.pos >= 64) & pt.domain.isin(["prose", "code"])].copy()
pt["gain_c"] = pt.nll_S - pt.nll_L; pt["gain_m"] = pt.nll_Ss - pt.nll_S
dm = pt.assign(dec=pd.qcut(pt.H_Ss, 10, labels=False) + 1).groupby("dec").agg(
    H=("H_Ss", "mean"), gain=("gain_m", "mean"), H_full=("H_S", "mean"))
dc = pt.assign(dec=pd.qcut(pt.H_S, 10, labels=False) + 1).groupby("dec").agg(
    H=("H_S", "mean"), gain=("gain_c", "mean"), H_big=("H_L", "mean"))
dm.to_csv(OUT / "deciles_memory.csv"); dc.to_csv(OUT / "deciles_compute.csv")
summary = {"n_tokens_natural": int(len(pt)),
           "spearman_Hss_gain_m": float(pt[["H_Ss", "gain_m"]].corr(method="spearman").iloc[0, 1]),
           "spearman_Hs_gain_c": float(pt[["H_S", "gain_c"]].corr(method="spearman").iloc[0, 1]),
           "spearman_Hs_KL_LS": float(pt[["H_S", "KL_LS"]].corr(method="spearman").iloc[0, 1])}
json.dump(summary, open(OUT / "pilot_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
P = pd.DataFrame(prow)
print(P[P.pool == "natural"].to_string(index=False))
