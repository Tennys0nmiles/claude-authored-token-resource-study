"""Statistics for the v2 GPU runs (e2e_v2.py): end-to-end gating over 5 document splits, Qwen2.5 at 8k tokens,
the which-vs-whether block-selection comparison, and the attention microbenchmark. Reads per-document CSVs, runs no
model, and writes analysis/stats/v2_*.csv.

Uncertainty: a document-level cluster bootstrap with 2,000 resamples. A resampled document contributes all of its
test-split instances, so the intervals cover document-to-document variation across the pooled splits. Comparisons
between gates use the same resamples (paired).
Pools: natural = papers + code; papers26 = papers first posted in September 2026 (arXiv ids 2609.*), which postdate
every model's training data; code; ids = papers with injected identifiers."""
import zlib   # bootstrap seeds from crc32: Python's hash() of strings changes between runs
import glob, json, pathlib, re, sys
import numpy as np
import pandas as pd

ML = pathlib.Path(__file__).resolve().parents[2]
IN = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ML / "gpu_results_session3"
OUT = ML / "analysis" / "stats"; OUT.mkdir(exist_ok=True)
NB = 2000
POOLS = {"natural": lambda d: d.domain.isin(["prose", "code"]),
         "papers26": lambda d: (d.domain == "prose") & d.doc.str.startswith("2609"),
         "code": lambda d: d.domain == "code",
         "ids": lambda d: d.domain == "prose_ids"}
NAMES = {"pythia-160m-deduped": "Pythia-160M", "pythia-410m-deduped": "Pythia-410M", "pythia-1.4b-deduped": "Pythia-1.4B",
         "Qwen2.5-1.5B": "Qwen2.5-1.5B", "Qwen2.5-7B": "Qwen2.5-7B"}


def parse(tag):
    m = re.match(r"e2e2_(.+)_T(\d+)_W(\d+)", tag)
    return NAMES.get(m.group(1), m.group(1)), int(m.group(2)), int(m.group(3))


def far_weight(n):                       # far keys summed over scored queries (positions W-1 .. W+n-2)
    return (n - 1) * (n - 2) / 2.0


def boot_matrix(ndocs, seed):
    rng = np.random.default_rng(seed)
    return np.stack([np.bincount(rng.integers(0, ndocs, ndocs), minlength=ndocs) for _ in range(NB)])   # [NB, docs]


def per_doc(df, keys):
    """Sum num/den over splits per document for each key combination -> {key: (num[d], den[d])} aligned on docs."""
    docs = sorted(df.doc.unique()); pos = {d: i for i, d in enumerate(docs)}
    out = {}
    for k, g in df.groupby(keys):
        num = np.zeros(len(docs)); den = np.zeros(len(docs))
        a = g.groupby("doc")[["gain_g", "gain_f"]].sum()
        ix = [pos[d] for d in a.index]
        num[ix] = a.gain_g.values; den[ix] = a.gain_f.values
        out[k] = (num, den)
    return docs, out


def ci(x):
    return np.percentile(x, 2.5), np.percentile(x, 97.5)


def main():
    summ, paired, meta, prop, blocks, bpaired, persplit, matched = [], [], [], [], [], [], [], []
    files = sorted(f for f in glob.glob(str(IN / "**" / "e2e2_*.csv"), recursive=True) if "_blocks" not in pathlib.Path(f).name)
    for f in files:
        tag = pathlib.Path(f).stem
        model, T, W = parse(tag)
        cfg = f"{model}, {T // 1024}k, W={W}"
        R = pd.read_csv(f)
        R["gain_g"] = R.nllA - R.nllG; R["gain_f"] = R.nllA - R.nllF; R["gain_i"] = R.nllA - R.nll_indep
        splits = sorted(R.split.unique())
        u = R[(R.policy == "random") & np.isclose(R.budget, 0.1)].drop_duplicates("doc")
        nat = u[u.domain.isin(["prose", "code"])]
        meta.append(dict(config=cfg, model=model, T=T, W=W, splits=len(splits), docs_natural=len(nat),
                         docs_papers26=int(((nat.domain == "prose") & nat.doc.str.startswith("2609")).sum()),
                         docs_ids=int((u.domain == "prose_ids").sum()), tokens_natural=int(nat.n.sum()),
                         local_loss=nat.nllA.sum() / nat.n.sum(), full_loss=nat.nllF.sum() / nat.n.sum(),
                         gap=(nat.nllA - nat.nllF).sum() / nat.n.sum()))
        for pool, sel in POOLS.items():
            D = R[sel(R)]
            if D.empty:
                continue
            docs, pdoc = per_doc(D, ["policy", "budget"])
            Bm = boot_matrix(len(docs), zlib.crc32(f"{cfg}|{pool}".encode()))
            boots = {}
            for (pol, b), (num, den) in pdoc.items():
                pt = 100 * num.sum() / den.sum(); bs = 100 * (Bm @ num) / (Bm @ den); boots[(pol, b)] = bs
                g = D[(D.policy == pol) & np.isclose(D.budget, b)]
                far = (g.far_frac * far_weight(g.n)).sum() / far_weight(g.n).sum()
                lo, hi = ci(bs)
                summ.append(dict(config=cfg, pool=pool, policy=pol, budget=b, point=pt, lo=lo, hi=hi, far_frac=far))
            for comp, (a, c, kind) in {"value/entropy": ("learned", "entropy", "ratio"),
                                       "hidden/entropy": ("hidden_only", "entropy", "ratio"),
                                       "rule/entropy": ("fam_rule", "entropy", "ratio"),
                                       "famhead/entropy": ("fam_head", "entropy", "ratio"),
                                       "familiarity contribution": ("learned", "hidden_only", "diff")}.items():
                if (a, 0.1) not in boots or (c, 0.1) not in boots:
                    continue
                x, y = boots[(a, 0.1)], boots[(c, 0.1)]
                na, da = pdoc[(a, 0.1)]; nc, dc = pdoc[(c, 0.1)]
                pa, pc = 100 * na.sum() / da.sum(), 100 * nc.sum() / dc.sum()
                val, bs = (pa / pc, x / y) if kind == "ratio" else (pa - pc, x - y)
                lo, hi = ci(bs)
                paired.append(dict(config=cfg, pool=pool, comparison=comp, value=val, lo=lo, hi=hi))
            if pool == "natural":
                for s in splits:                             # per-split ratio at 10%
                    Ds = D[D.split == s]
                    r = {p: 100 * Ds[(Ds.policy == p) & np.isclose(Ds.budget, 0.1)].gain_g.sum() /
                         Ds[(Ds.policy == p) & np.isclose(Ds.budget, 0.1)].gain_f.sum() for p in ("learned", "entropy")}
                    persplit.append(dict(config=cfg, split=s, value=r["learned"], entropy=r["entropy"],
                                         ratio=r["learned"] / r["entropy"]))
                for pol in ("entropy", "learned", "oracle"):
                    g = D[(D.policy == pol) & np.isclose(D.budget, 0.1)]
                    prop.append(dict(config=cfg, policy=pol, e2e=100 * g.gain_g.sum() / g.gain_f.sum(),
                                     indep=100 * g.gain_i.sum() / g.gain_f.sum()))
        fbs = sorted(glob.glob(f[:-4] + "_blocks*.csv"))      # default and recurrence-addressed conditions
        if fbs:
            Bk = pd.concat([pd.read_csv(x) for x in fbs]); Bk = Bk[Bk.domain.isin(["prose", "code"])].copy()
            Bk["gain_g"] = Bk.nllA - Bk.nllG; Bk["gain_f"] = Bk.nllA - Bk.nllF
            Bk["key"] = (Bk.cond + "|" + Bk.scorer.fillna("") + "|" + Bk.gate_policy.fillna("") + "|" +
                         Bk.b.fillna(-1).round(3).astype(str) + "|" + Bk.rho.fillna(-1).round(3).astype(str))
            G = R[(R.split == Bk.split.iloc[0]) & R.domain.isin(["prose", "code"]) & R.policy.isin(["learned", "entropy", "oracle"])].copy()
            G["key"] = "gate-only|sdpa|" + G.policy + "|" + G.budget.round(3).astype(str) + "|-1.0"
            G["touch_frac"] = G.budget
            allk = pd.concat([Bk[["doc", "n", "key", "gain_g", "gain_f", "far_frac", "touch_frac"]],
                              G[["doc", "n", "key", "gain_g", "gain_f", "far_frac", "touch_frac"]]])
            docs, pdoc = per_doc(allk, ["key"])
            Bm = boot_matrix(len(docs), zlib.crc32(f"{cfg}|blocks".encode()))
            bb = {}
            for (k,), (num, den) in ((k if isinstance(k, tuple) else (k,), v) for k, v in pdoc.items()):
                g = allk[allk.key == k]
                bs = 100 * (Bm @ num) / (Bm @ den); bb[k] = (100 * num.sum() / den.sum(), bs)
                lo, hi = ci(bs)
                cond, scorer, gp, b, rho = k.split("|")
                blocks.append(dict(config=cfg, cond=cond, scorer=scorer, gate_policy=gp, b=float(b), rho=float(rho),
                                   R=bb[k][0], lo=lo, hi=hi,
                                   far_frac=(g.far_frac * far_weight(g.n)).sum() / far_weight(g.n).sum(),
                                   touch_frac=(g.touch_frac * g.n).sum() / g.n.sum()))
            # matched-budget test: each condition against the Quest-style curve (every query), interpolated at the
            # condition's own far-key fraction within every bootstrap resample; the curve starts at (0, 0)
            fn = {}
            for kk, g in allk.groupby("key"):
                a_ = g.assign(fw=g.far_frac * far_weight(g.n), fd=far_weight(g.n)).groupby("doc")[["fw", "fd"]].sum()
                x1 = np.zeros(len(docs)); x2 = np.zeros(len(docs)); ix = [docs.index(d) for d in a_.index]
                x1[ix] = a_.fw.values; x2[ix] = a_.fd.values; fn[kk] = (x1, x2)
            qkeys = sorted([kk for kk in bb if kk.startswith("block|quest|")], key=lambda kk: float(kk.split("|")[4]))
            if qkeys:
                Rq = np.stack([bb[kk][1] for kk in qkeys]); Fq = np.stack([100 * (Bm @ fn[kk][0]) / (Bm @ fn[kk][1]) for kk in qkeys])
                Rq0 = np.array([bb[kk][0] for kk in qkeys]); Fq0 = np.array([100 * fn[kk][0].sum() / fn[kk][1].sum() for kk in qkeys])
                for kk in bb:
                    if kk.startswith("block|"):
                        continue
                    Fc = 100 * (Bm @ fn[kk][0]) / (Bm @ fn[kk][1]); Fc0 = 100 * fn[kk][0].sum() / fn[kk][1].sum()
                    interp = np.array([np.interp(Fc[i], np.r_[0, Fq[:, i]], np.r_[0, Rq[:, i]]) for i in range(NB)])
                    d_ = bb[kk][1] - interp; lo, hi = ci(d_)
                    matched.append(dict(config=cfg, condition=kk, far_pct=Fc0, R=bb[kk][0],
                                        quest_at_same_budget=float(np.interp(Fc0, np.r_[0, Fq0], np.r_[0, Rq0])),
                                        diff=bb[kk][0] - float(np.interp(Fc0, np.r_[0, Fq0], np.r_[0, Rq0])), lo=lo, hi=hi))
            for name, a, c in (("value vs entropy gate, +Quest (30% x 1/3)", "gate+block|quest|learned|0.3|0.333", "gate+block|quest|entropy|0.3|0.333"),
                               ("value vs entropy gate, +Quest (20% x 1/2)", "gate+block|quest|learned|0.2|0.5", "gate+block|quest|entropy|0.2|0.5"),
                               ("value gate +Quest (30% x 1/3) vs Quest for all queries (10%)", "gate+block|quest|learned|0.3|0.333", "block|quest||-1.0|0.1"),
                               ("value gate only (10%) vs Quest for all queries (10%)", "gate-only|sdpa|learned|0.1|-1.0", "block|quest||-1.0|0.1"),
                               ("recurrence-addressed only vs Quest at its smallest budget (rho 0.5%)", "recur|recur||-1.0|0.0", "block|quest||-1.0|0.005"),
                               ("recurrence-addressed only vs value gate only (10%)", "recur|recur||-1.0|0.0", "gate-only|sdpa|learned|0.1|-1.0"),
                               ("recurrence blocks added to Quest 2.5% vs Quest 2.5% alone", "recur+quest|recur+quest||-1.0|0.025", "block|quest||-1.0|0.025"),
                               ("recurrence blocks added to Quest 5% vs Quest 5% alone", "recur+quest|recur+quest||-1.0|0.05", "block|quest||-1.0|0.05")):
                if a in bb and c in bb:
                    lo, hi = ci(bb[a][1] - bb[c][1])
                    bpaired.append(dict(config=cfg, comparison=name, diff=bb[a][0] - bb[c][0], lo=lo, hi=hi))
    for name, rows in (("v2_e2e_summary", summ), ("v2_e2e_paired", paired), ("v2_e2e_meta", meta),
                       ("v2_propagation", prop), ("v2_blocks", blocks), ("v2_blocks_paired", bpaired),
                       ("v2_persplit", persplit), ("v2_blocks_matched", matched)):
        pd.DataFrame(rows).to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(rows), "rows")
    bj = list(IN.glob("**/attn_bench.json"))
    if bj:
        b = json.load(open(bj[0])); pd.DataFrame(b["rows"]).to_csv(OUT / "v2_bench.csv", index=False)
        json.dump({k: v for k, v in b.items() if k != "rows"}, open(OUT / "v2_bench_meta.json", "w"), indent=1)
        print("bench", len(b["rows"]), "rows")


if __name__ == "__main__":
    main()
