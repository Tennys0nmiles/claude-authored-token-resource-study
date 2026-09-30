"""Follow-up to Experiment B: can a cheap *familiarity* signal tell the memory controller
when long-range context will help?

A model restricted to a 32-63-token window cannot know whether the current token sequence
appeared earlier in the document. Biology separates fast, cheap *familiarity* ("seen this
before") from slow *recollection* (retrieving the episode). The ML analogue is an O(1)-per-
token membership test of the local n-gram against a hashed index of the long context
(cf. Engram-style hashed n-gram lookup): no attention over the long context is needed.

Familiarity features for target t (predicting token t+1), computed only from tokens that are
already visible (ids[0..t]) and only against the region *outside* the local window:
  fam_bi / fam_tri / fam_quad    local 2/3/4-gram ending at t occurred earlier
  fam_bi_det                     ... and every earlier occurrence had the same continuation
  log counts of the bigram and of the current token in the earlier region
Also refits the entropy-decile table (natural docs only) for the report.
"""
import json, pathlib
import numpy as np
import pandas as pd
import analyze as A

RES = A.RES
WIN0 = 31  # a target t >= 63 sees the window starting at s = 32*floor((t-31)/32)


def familiarity_features(df):
    feats = np.zeros((len(df), 6), dtype=np.float32)
    for doc, g in df.groupby("doc", sort=False):
        idx = g.index.values
        ids = SEQS[doc]   # full token sequence of the document ([BOS] + targets), built in main()
        bi, tri, quad, uni = {}, {}, {}, {}
        added = 0                                    # earlier region = ids[0:added]
        for r, pos in zip(idx, g.pos.values):
            t = pos - 1                              # target index; context ends at ids[t]
            s = 32 * ((t - WIN0) // 32)              # start of this target's local window
            while added < s:                         # extend the hashed index up to s
                i = added
                uni[ids[i]] = uni.get(ids[i], 0) + 1
                if i >= 1:
                    k = (ids[i - 1], ids[i])
                    nxt = ids[i + 1] if i + 1 < s else None
                    e = bi.setdefault(k, [0, set()]); e[0] += 1
                    if nxt is not None: e[1].add(nxt)
                if i >= 2: tri[(ids[i - 2], ids[i - 1], ids[i])] = 1
                if i >= 3: quad[(ids[i - 3], ids[i - 2], ids[i - 1], ids[i])] = 1
                added += 1
            kb = (ids[t - 1], ids[t])
            e = bi.get(kb)
            feats[r] = (e is not None,
                        (ids[t - 2], ids[t - 1], ids[t]) in tri,
                        (ids[t - 3], ids[t - 2], ids[t - 1], ids[t]) in quad,
                        e is not None and len(e[1]) == 1,
                        np.log1p(e[0]) if e else 0.0,
                        np.log1p(uni.get(ids[t], 0)))
    return feats


def main():
    global SEQS
    raw = pd.read_parquet(RES / "per_token.parquet", columns=["doc", "pos", "tok"])
    SEQS = {d: np.concatenate([[0], g.sort_values("pos").tok.values])   # [BOS] + targets
            for d, g in raw.groupby("doc")}
    df, XA, XB = A.load()
    Fam = familiarity_features(df)
    names = ["fam_bi", "fam_tri", "fam_quad", "fam_bi_det", "log_bi_count", "log_tok_count"]
    for j, n in enumerate(names):
        df[n] = Fam[:, j]
    XBf = np.hstack([XB, Fam])
    Xscal = np.hstack([df[["H_Ss"]].values.astype(np.float32), Fam])
    rows, sel = [], []
    for seed in A.SEEDS:
        train_docs, tr, te = A.split(df, seed)
        T = df[te].reset_index(drop=True)
        sc = {"entropy (FLARE-style)": T.H_Ss.values}
        sc["learned: value (KL)"], _ = A.fit_predict(XB, df.KL_SSs.values, df, train_docs, tr, te, seed)
        sc["learned: value (KL) + familiarity"], _ = A.fit_predict(XBf, df.KL_SSs.values, df, train_docs, tr, te, seed)
        sc["familiarity + entropy only (7 scalars)"], _ = A.fit_predict(Xscal, df.KL_SSs.values, df, train_docs, tr, te, seed)
        sc["oracle: KL (needs resource)"] = T.KL_SSs.values
        for pool in A.POOLS:
            m = (T.domain.isin(["prose", "code"]) if pool == "natural" else T.domain == pool).values
            g = T.gain_m.values[m]
            for pol, s in sc.items():
                for b in A.BUDGETS:
                    r, ix = A.recovered(s[m], g, b)
                    rows.append(dict(seed=seed, pool=pool, policy=pol, budget=b, R=r))
                    if b == 0.10 and pool == "prose_ids":
                        sub = T[m].iloc[ix]
                        sel.append(dict(seed=seed, policy=pol,
                                        share_id_first=(sub.label == "id_first").mean(),
                                        share_id_repeat=(sub.label == "id_repeat").mean()))
                rows.append(dict(seed=seed, pool=pool, policy=pol, budget="b50",
                                 R=A.budget_for_half(s[m], g)))
        print("seed", seed, "done", flush=True)
    R = pd.DataFrame(rows); R.to_csv(RES / "B_memory_familiarity.csv", index=False)
    S = pd.DataFrame(sel).groupby("policy").mean().drop(columns="seed")
    # how often do the familiarity bits fire, and what is the memory gain when they do?
    nat = df[df.domain.isin(["prose", "code"])]
    fire = {n: dict(rate=float(nat[n].gt(0).mean()),
                    gain_m_when_on=float(nat.loc[nat[n] > 0, "gain_m"].mean()),
                    gain_m_when_off=float(nat.loc[nat[n] == 0, "gain_m"].mean()))
            for n in ["fam_bi", "fam_tri", "fam_quad", "fam_bi_det"]}
    ids_ = df[df.domain == "prose_ids"]
    fire_ids = ids_.groupby("label")[["fam_bi", "fam_tri", "fam_bi_det"]].mean().round(3)
    b50 = R[R.budget == "b50"].groupby(["pool", "policy"]).R.agg(["mean", "std"])
    Rb = R[R.budget != "b50"].copy(); Rb["budget"] = Rb.budget.astype(float)
    piv = (Rb.groupby(["pool", "policy", "budget"]).R.mean().unstack("budget") * 100).round(1)
    piv.columns = [f"R@{int(round(100*c))}%" for c in piv.columns]
    piv["budget for 50% of gap"] = (100 * b50["mean"]).round(1).astype(str) + "% ± " + \
                                   (100 * b50["std"]).round(1).astype(str)
    md = ["### B_memory + familiarity: % of long-context gain recovered (mean of 5 doc splits)\n",
          piv.to_markdown(),
          "\n\n### Selection at 10% budget on id-injected prose (base rates: id_first 3.9%, id_repeat 1.0%)\n",
          S.round(3).to_markdown(),
          "\n\n### Familiarity bits on natural text: firing rate and mean memory gain (nats) when on/off\n",
          pd.DataFrame(fire).T.round(3).to_markdown(),
          "\n\n### Familiarity bits by token type on id-injected prose (fraction firing)\n",
          fire_ids.to_markdown()]
    (RES / "tables_familiarity.md").write_text("\n".join(md) + "\n")
    # cross-domain transfer: train on one natural domain, test on the other
    xrows = []
    for seed in A.SEEDS:
        train_docs, tr, te = A.split(df, seed)
        for src, dst in (("prose", "code"), ("code", "prose")):
            tr_s = tr & (df.domain == src).values
            docs_s = [d for d in train_docs if d in set(df.loc[df.domain == src, "base"])]
            te_d = te & (df.domain == dst).values
            T = df[te_d].reset_index(drop=True); g = T.gain_m.values
            cand = {"entropy": T.H_Ss.values}
            for nm, X in (("learned + familiarity", XBf), ("familiarity + entropy (7 scalars)", Xscal)):
                cand[f"{nm}, trained on {src}"], _ = A.fit_predict(X, df.KL_SSs.values, df, docs_s, tr_s, te_d, seed)
            for pol, s_ in cand.items():
                xrows.append(dict(seed=seed, test_domain=dst, policy=pol.replace(f", trained on {src}", " (other domain)"),
                                  R10=A.recovered(s_, g, 0.10)[0], b50=A.budget_for_half(s_, g)))
    X_ = pd.DataFrame(xrows).groupby(["test_domain", "policy"])[["R10", "b50"]].mean()
    X_ = (100 * X_).round(1); X_.columns = ["% gain recovered @10%", "budget for 50% (%)"]
    md += ["\n\n### Cross-domain transfer (train on the other natural domain)\n", X_.to_markdown()]
    (RES / "tables_familiarity.md").write_text("\n".join(md) + "\n")
    A.deciles(df).to_csv(RES / "entropy_deciles.csv")
    print("\n".join(md))


if __name__ == "__main__":
    main()
