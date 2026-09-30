"""Analysis: is surprise (entropy) a good signal for WHERE to spend extra resources?

Experiment A (compute):  base = S with full context; resource = the bigger model L.
    per-token value  gain_c = nll_S - nll_L        (smooth version: KL(p_L || p_S))
    cheap features   S hidden states (layers 6, 12) + S entropy/logit-lens scalars
Experiment B (memory read / retrieval):  base = S with a 32-63 token window;
    resource = full document context.
    per-token value  gain_m = nll_Ss - nll_S       (smooth version: KL(p_S || p_Ss))
    cheap features   S hidden states computed on the short window + short-window entropy

Allocation policies choose a budget fraction b of tokens to receive the resource:
    random | entropy (BLT/FLARE-style) | learned raw-surprise head (control: same features,
    same training, but predicts the loss itself) | learned value heads (predict realized
    gain or KL) | oracles (use the expensive model; not realizable).
Metric: fraction of the total loss gap recovered, R(b) = sum_selected gain / sum_all gain.
Train/test split by source document (5 random splits); an id-injected document always
shares the split of the document it was made from.
"""
import json, pathlib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge

ROOT = pathlib.Path(__file__).parent
import os
RES = pathlib.Path(os.environ.get("PILOT_RES", ROOT / "results"))
BUDGETS = [0.02, 0.05, 0.10, 0.20, 0.30, 0.50]
SEEDS = range(5)
POOLS = ["natural", "prose", "code", "prose_ids"]   # natural = prose + code


def load():
    df = pd.read_parquet(RES / "per_token.parquet")
    FS = np.load(RES / "feats_S.npy", mmap_mode="r")
    FSs = np.load(RES / "feats_Ss.npy", mmap_mode="r")
    keep = (df.pos >= 64).values           # short and full context differ only from here on
    df = df[keep].reset_index(drop=True)
    idx = np.flatnonzero(keep)
    XA = np.hstack([np.asarray(FS[idx], dtype=np.float32),
                    df[["H_S", "H_S6", "KL_S_S6", "pmax_S"]].values.astype(np.float32)])
    XB = np.hstack([np.asarray(FSs[idx], dtype=np.float32),
                    df[["H_Ss"]].values.astype(np.float32)])
    df["conf_gap"] = 1 - df.pmax_S
    df["gain_c"] = df.nll_S - df.nll_L
    df["gain_m"] = df.nll_Ss - df.nll_S
    df["base"] = df.doc_id.str.replace("+ids", "", regex=False)
    return df, XA, XB


def split(df, seed):
    """Half of the source documents of each domain go to train. Returns (train_docs, train
    mask over natural tokens only, test mask over all tokens incl. id-injected copies)."""
    rng = np.random.default_rng(seed)
    train = []
    for dom in ("prose", "code"):
        b = sorted(df.loc[df.domain == dom, "base"].unique())
        rng.shuffle(b)
        train += b[: len(b) // 2]
    in_train = df.base.isin(set(train)).values
    natural_doc = df.domain.isin(["prose", "code"]).values
    return train, in_train & natural_doc, ~in_train


def fit_predict(X, y, df, train_docs, tr, te, seed, alphas=(10.0, 100.0, 1000.0, 10000.0)):
    """Ridge on standardized features. Trained on natural-text train documents only;
    alpha picked on a random 20% of those documents held out."""
    mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
    Z = (X - mu) / sd
    rng = np.random.default_rng(1000 + seed)
    val_docs = set(rng.choice(train_docs, size=max(1, len(train_docs) // 5), replace=False))
    is_val = df.base.isin(val_docs).values
    fit_i, val_i = np.flatnonzero(tr & ~is_val), np.flatnonzero(tr & is_val)
    best = min(alphas, key=lambda a: np.mean(
        (Ridge(alpha=a).fit(Z[fit_i], y[fit_i]).predict(Z[val_i]) - y[val_i]) ** 2))
    return Ridge(alpha=best).fit(Z[np.flatnonzero(tr)], y[np.flatnonzero(tr)]).predict(Z[te]), best


def recovered(score, gain, b):
    k = max(1, int(round(b * len(score))))
    sel = np.argsort(-score, kind="stable")[:k]
    return gain[sel].sum() / gain.sum(), sel


def budget_for_half(score, gain):
    order = np.argsort(-score, kind="stable")
    c = np.cumsum(gain[order]) / gain.sum()
    hit = np.flatnonzero(c >= 0.5)
    return (hit[0] + 1) / len(score) if len(hit) else np.nan


def experiment(df, X, spec):
    """spec: dict(name, gain, kl, raw, signals={name: column}) -> per-seed results."""
    rows, sel_rows, corr_rows = [], [], []
    for seed in SEEDS:
        train_docs, tr, te = split(df, seed)
        T = df[te].reset_index(drop=True)
        scores = {k: T[c].values for k, c in spec["signals"].items()}
        for tgt, col in (("learned: raw surprise", spec["raw"]),
                         ("learned: value (realized gain)", spec["gain"]),
                         ("learned: value (KL)", spec["kl"])):
            scores[tgt], _ = fit_predict(X, df[col].values, df, train_docs, tr, te, seed)
        if spec.get("scalars"):
            # ablation: the same value head from a handful of scalar features only
            Xs = df[spec["scalars"]].values.astype(np.float32)
            scores["learned: value (KL), scalars only"], _ = fit_predict(
                Xs, df[spec["kl"]].values, df, train_docs, tr, te, seed)
        scores["oracle: KL (needs resource)"] = T[spec["kl"]].values
        scores["oracle: realized gain"] = T[spec["gain"]].values
        rng = np.random.default_rng(100 + seed)
        scores["random"] = rng.random(len(T))
        for pool in POOLS:
            m = (T.domain.isin(["prose", "code"]) if pool == "natural" else T.domain == pool).values
            g = T[spec["gain"]].values[m]
            for pol, s in scores.items():
                s_ = s[m]
                for b in BUDGETS:
                    r, sel = recovered(s_, g, b)
                    rows.append(dict(seed=seed, pool=pool, policy=pol, budget=b, R=r))
                    if b == 0.10:
                        sub = T[m].iloc[sel]
                        sel_rows.append(dict(seed=seed, pool=pool, policy=pol,
                                             share_id_first=(sub.label == "id_first").mean(),
                                             share_id_repeat=(sub.label == "id_repeat").mean(),
                                             share_no_gain=(sub[spec["gain"]] <= 0.05).mean(),
                                             mean_gain=sub[spec["gain"]].mean(),
                                             mean_H_L=sub.H_L.mean()))
                rows.append(dict(seed=seed, pool=pool, policy=pol, budget="b50",
                                 R=budget_for_half(s_, g)))
            if pool in ("natural", "prose", "code"):
                for pol in list(spec["signals"]) + ["learned: value (KL)", "learned: raw surprise"]:
                    corr_rows.append(dict(seed=seed, pool=pool, signal=pol,
                                          rho_gain=spearmanr(scores[pol][m], g).statistic,
                                          rho_kl=spearmanr(scores[pol][m], T[spec["kl"]].values[m]).statistic))
        print(spec["name"], "seed", seed, "done", flush=True)
    return pd.DataFrame(rows), pd.DataFrame(sel_rows), pd.DataFrame(corr_rows)


def cross_domain(df, X, spec):
    """Train the value head on one domain's train docs, test on the other domain's test docs."""
    rows = []
    for seed in SEEDS:
        train_docs, tr, te = split(df, seed)
        for src, dst in (("prose", "code"), ("code", "prose")):
            tr_s = tr & (df.domain == src).values
            docs_s = [d for d in train_docs if d in set(df.loc[df.domain == src, "base"])]
            te_d = te & (df.domain == dst).values
            T = df[te_d].reset_index(drop=True)
            g = T[spec["gain"]].values
            learned, _ = fit_predict(X, df[spec["kl"]].values, df, docs_s, tr_s, te_d, seed)
            ent = T[list(spec["signals"].values())[0]].values
            for pol, sc in (("entropy", ent), (f"learned on {src} only", learned)):
                rows.append(dict(seed=seed, test_domain=dst, policy=pol,
                                 R10=recovered(sc, g, 0.10)[0], R20=recovered(sc, g, 0.20)[0],
                                 b50=budget_for_half(sc, g)))
    return pd.DataFrame(rows)


def deciles(df):
    d = df[df.domain.isin(["prose", "code"])].copy()   # natural documents only (no id-injected copies)
    d["H_S_decile"] = pd.qcut(d.H_S, 10, labels=False) + 1
    return d.groupby("H_S_decile").agg(H_S=("H_S", "mean"), nll_S=("nll_S", "mean"),
                                       H_L=("H_L", "mean"), gain_c=("gain_c", "mean"),
                                       KL_LS=("KL_LS", "mean"), gain_m=("gain_m", "mean"),
                                       n=("H_S", "size")).round(3)


def main():
    df, XA, XB = load()
    print("tokens analysed:", len(df), df.groupby(["domain", "label"]).size().to_dict())
    A = dict(name="A_compute", gain="gain_c", kl="KL_LS", raw="nll_S",
             signals={"entropy (BLT-style)": "H_S", "1 - max prob (CALM-style)": "conf_gap",
                      "layer-6 to layer-12 change": "KL_S_S6"},
             scalars=["H_S", "H_S6", "KL_S_S6", "pmax_S"])
    B = dict(name="B_memory", gain="gain_m", kl="KL_SSs", raw="nll_Ss",
             signals={"entropy (FLARE-style)": "H_Ss"})
    out = {}
    for spec, X in ((A, XA), (B, XB)):
        R, SEL, COR = experiment(df, X, spec)
        R.to_csv(RES / f"{spec['name']}_budget_curves.csv", index=False)
        SEL.to_csv(RES / f"{spec['name']}_selection_at_10pct.csv", index=False)
        COR.to_csv(RES / f"{spec['name']}_rank_correlations.csv", index=False)
        cross_domain(df, X, spec).to_csv(RES / f"{spec['name']}_cross_domain.csv", index=False)
        out[spec["name"]] = (R, SEL, COR)
    deciles(df).to_csv(RES / "entropy_deciles.csv")
    summary = {"n_tokens": int(len(df)),
               "domain_label_counts": {f"{a}/{b}": int(n) for (a, b), n in
                                       df.groupby(["domain", "label"]).size().items()},
               "mean_nll": df.groupby("domain")[["nll_S", "nll_L", "nll_Ss"]].mean().round(4).to_dict()}
    json.dump(summary, open(RES / "summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
