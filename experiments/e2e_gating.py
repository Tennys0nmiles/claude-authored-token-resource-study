"""End-to-end test of pre-fetch gating for long-range attention in a frozen LM.

Every query position attends to a local window of W keys (plus the first token, an
"attention sink"). A gated query additionally attends to the entire prefix. The gate is
decided *before* any long-range attention is computed, from one of:

  random                  budget-matched control
  entropy                 entropy of a cheap local-only pass (FLARE-style trigger)
  familiarity rule        no training at all: does the local 4/3/2-gram ending here occur
                          earlier in the document, outside the window? (hashed lookup, O(1))
  familiarity head        ridge on entropy + 6 familiarity numbers (7 scalars)
  learned head            ridge on local-pass hidden states + entropy + familiarity
  oracle                  KL(full || local) at that position (needs the full pass)

Unlike the per-token pilot, this is a real forward pass with mixed attention in every layer,
so information that gated tokens fetch can propagate to later, ungated neighbours.

Metric: fraction of the local→full loss gap recovered, over tokens with position >= W,
as a function of the fraction of those tokens that are gated. Usage:
    python e2e_gating.py <hf-model-name> <W> [n_seeds]
"""
import json, sys, time, pathlib, random
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

ROOT = pathlib.Path(__file__).parent
import os
RES = pathlib.Path(os.environ.get("PILOT_RES", ROOT / "results")); RES.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(10)
DEV = torch.device(os.environ.get('DEV', 'cuda' if torch.cuda.is_available() else 'cpu'))
DOCS = pathlib.Path(os.environ.get("DOCS", ROOT / "data" / "docs.jsonl"))

NAME = sys.argv[1] if len(sys.argv) > 1 else "EleutherAI/pythia-160m-deduped"
W = int(sys.argv[2]) if len(sys.argv) > 2 else 64
SEED = 0
T = int(os.environ.get("T_TOK", "1024"))
BUDGETS = [0.05, 0.10, 0.20, 0.30]
FEAT_LAYERS = None  # set after model load: (mid, last)

# re-use the document list / id injection / split exactly as in the pilot
src = (ROOT / "collect.py").read_text()
import types
C = types.ModuleType("c"); C.__file__ = str(ROOT / "collect.py")
exec(src[: src.index("tok = AutoTokenizer")] + src[src.index("def clean(text):"): src.index("def _stats(")], C.__dict__)

tok = AutoTokenizer.from_pretrained(NAME)
M = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32).eval().to(DEV)
BOS = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
nl = M.config.num_hidden_layers
FEAT_LAYERS = (nl // 2, nl)


def jobs():
    docs = [json.loads(l) for l in open(DOCS)]
    rng = random.Random(1)
    out = [(d["id"], d["domain"], C.clean(d["text"]), []) for d in docs]
    for d in docs:
        if d["domain"] == "prose":
            txt, spans = C.inject_ids(C.clean(d["text"]), rng)
            if txt:
                out.append((d["id"] + "+ids", "prose_ids", txt, spans))
    return out


def split_docs(all_jobs, seed):
    rng = np.random.default_rng(seed)
    train = []
    for dom in ("prose", "code"):
        b = sorted({j[0] for j in all_jobs if j[1] == dom})
        rng.shuffle(b)
        train += b[: len(b) // 2]
    return set(train)


def familiarity(ids):
    """6 familiarity numbers per target index t (context ends at ids[t]); earlier region
    excludes the local window: positions < t-W+1."""
    n = len(ids)
    out = np.zeros((n - 1, 6), np.float32)
    bi, tri, quad, uni = {}, set(), set(), {}
    added = 0
    for t in range(n - 1):
        lim = t - W + 1
        while added < lim:
            i = added
            uni[ids[i]] = uni.get(ids[i], 0) + 1
            if i >= 1:
                e = bi.setdefault((ids[i - 1], ids[i]), [0, set()]); e[0] += 1
                if i + 1 < lim: e[1].add(ids[i + 1])
            if i >= 2: tri.add((ids[i - 2], ids[i - 1], ids[i]))
            if i >= 3: quad.add((ids[i - 3], ids[i - 2], ids[i - 1], ids[i]))
            added += 1
        if t < 3:
            continue
        e = bi.get((ids[t - 1], ids[t]))
        out[t] = (e is not None, (ids[t - 2], ids[t - 1], ids[t]) in tri,
                  (ids[t - 3], ids[t - 2], ids[t - 1], ids[t]) in quad,
                  e is not None and len(e[1]) == 1,
                  np.log1p(e[0]) if e else 0.0, np.log1p(uni.get(ids[t], 0)))
    return out


def masks(n, gated_rows):
    """[B,1,n,n] boolean masks; gated_rows: list of bool arrays over query positions."""
    i = torch.arange(n, device=DEV)[:, None]; j = torch.arange(n, device=DEV)[None, :]
    causal = j <= i
    local = causal & ((i - j < W) | (j == 0))
    out = []
    for g in gated_rows:
        g = torch.as_tensor(g, device=DEV)[:, None]
        out.append(torch.where(g, causal, local))
    return torch.stack(out)[:, None]


@torch.inference_mode()
def run(ids, mask_batch, want_hidden=False):
    x = ids[None].expand(mask_batch.shape[0], -1)
    o = M(x, attention_mask=mask_batch, output_hidden_states=want_hidden)
    lp = F.log_softmax(o.logits[:, :-1].float(), -1)
    return lp, (o.hidden_states if want_hidden else None)


@torch.inference_mode()
def run_nll(ids, mask_batch):
    """Per-target NLL only (no full log-softmax copy): [B, n-1]."""
    x = ids[None].expand(mask_batch.shape[0], -1)
    logits = M(x, attention_mask=mask_batch).logits[:, :-1].float()
    y = ids[1:][None, :, None].expand(logits.shape[0], -1, 1)
    return (torch.logsumexp(logits, -1) - logits.gather(2, y)[..., 0]).cpu().numpy()


def main():
    J = jobs()
    train_docs = split_docs(J, SEED)
    rows_tr, rows_te = [], []
    t0 = time.time()
    # ---------- pass 1: local + full passes for every document (features and targets)
    per_doc = {}
    for k, (did, dom, text, spans) in enumerate(J):
        ids = [BOS] + tok(text, add_special_tokens=False)["input_ids"][:T]
        if len(ids) < 256:
            continue
        ids_t = torch.tensor(ids, device=DEV); n = len(ids)
        allfalse = np.zeros(n, bool); alltrue = np.ones(n, bool)
        lp, hs = run(ids_t, masks(n, [allfalse, alltrue]), want_hidden=True)
        lpA, lpF = lp[0], lp[1]
        y = ids_t[1:]
        nllA = -lpA.gather(1, y[:, None])[:, 0]; nllF = -lpF.gather(1, y[:, None])[:, 0]
        HA = -(lpA.exp() * lpA).sum(-1)
        KL = (lpF.exp() * (lpF - lpA)).sum(-1)
        feats = torch.cat([hs[l][0, :-1] for l in FEAT_LAYERS], -1).float().cpu().numpy().astype(np.float16)
        del hs
        fam = familiarity(ids)
        del lp, lpA, lpF
        per_doc[did] = dict(dom=dom, ids=ids_t, nllA=nllA.cpu().numpy(), nllF=nllF.cpu().numpy(),
                            HA=HA.cpu().numpy(), KL=KL.cpu().numpy(), feats=feats, fam=fam,
                            train=did in train_docs)
        if k % 20 == 0:
            print(f"[pass1 {k+1}/{len(J)}] {time.time()-t0:.0f}s", flush=True)
    # ---------- fit gates on train docs (natural docs only), positions >= W
    def stack(docs, key):
        return np.concatenate([per_doc[d][key][W - 1:] for d in docs])
    tr = [d for d, v in per_doc.items() if v["train"] and v["dom"] in ("prose", "code")]
    te = [d for d, v in per_doc.items() if not v["train"] and d.replace("+ids", "") not in train_docs]
    Xh = np.hstack([stack(tr, "feats").astype(np.float32), stack(tr, "HA")[:, None], stack(tr, "fam")])
    Xs = np.hstack([stack(tr, "HA")[:, None], stack(tr, "fam")])
    ytr = stack(tr, "KL")
    from sklearn.linear_model import Ridge

    def fit(X, y, alpha):
        mu, sd = X.mean(0), X.std(0) + 1e-6
        m = Ridge(alpha=alpha).fit((X - mu) / sd, y)
        return lambda Z: m.predict((Z - mu) / sd)
    head_full = fit(Xh, ytr, 1000.0)
    Xh_nofam = np.hstack([stack(tr, "feats").astype(np.float32), stack(tr, "HA")[:, None]])
    head_hidden = fit(Xh_nofam, ytr, 1000.0)          # ablation: no familiarity features
    head_7 = fit(Xs, ytr, 10.0)
    print(f"gates fitted on {len(tr)} docs; evaluating {len(te)} test docs", flush=True)
    # ---------- pass 2: gated forwards on test docs
    for k, d in enumerate(te):
        v = per_doc[d]; n = len(v["ids"]); idx = np.arange(W - 1, n - 1)   # targets with pos >= W
        Xh_d = np.hstack([v["feats"][idx].astype(np.float32), v["HA"][idx, None], v["fam"][idx]])
        Xs_d = np.hstack([v["HA"][idx, None], v["fam"][idx]])
        fam = v["fam"][idx]
        rng = np.random.default_rng(k)
        scores = {
            "random": rng.random(len(idx)),
            "entropy (local pass)": v["HA"][idx],
            "familiarity rule (no training)": 4 * fam[:, 2] + 2 * fam[:, 1] + fam[:, 0] + 0.01 * v["HA"][idx],
            "familiarity head (7 scalars)": head_7(Xs_d),
            "learned head (hidden + familiarity)": head_full(Xh_d),
            "learned head (hidden only, ablation)": head_hidden(np.hstack([v["feats"][idx].astype(np.float32), v["HA"][idx, None]])),
            "oracle KL (needs full pass)": v["KL"][idx],
        }
        base = dict(doc=d, domain=v["dom"], n=len(idx), nllA=float(v["nllA"][idx].sum()),
                    nllF=float(v["nllF"][idx].sum()))
        for pol, s in scores.items():
            order = np.argsort(-s, kind="stable")
            gated_sets = []
            for b in BUDGETS:
                g = np.zeros(n, bool)
                g[idx[order[: int(round(b * len(idx)))]] ] = True   # gate query rows (target index = row)
                gated_sets.append(g)
            # one mask per forward: batching 4 masks needed ~1 GB of logits and contributed to an OOM
            nll_batch = np.concatenate([run_nll(v["ids"], masks(n, [g_])) for g_ in gated_sets])
            for bi, b in enumerate(BUDGETS):
                nllG = nll_batch[bi]
                g = gated_sets[bi][:n - 1]
                indep = v["nllA"][idx].sum() - (v["nllA"][idx] - v["nllF"][idx])[g[idx]].sum()
                rows_te.append(dict(base, policy=pol, budget=b, nllG=float(nllG[idx].sum()),
                                    nll_indep=float(indep)))
        if k % 10 == 0:
            print(f"[pass2 {k+1}/{len(te)}] {time.time()-t0:.0f}s", flush=True)
    tag = f"{NAME.split('/')[-1]}_W{W}"
    R = pd.DataFrame(rows_te); R.to_csv(RES / f"e2e_{tag}.csv", index=False)
    out = []
    for pool, m in (("natural", R.domain.isin(["prose", "code"])), ("prose", R.domain == "prose"),
                    ("code", R.domain == "code"), ("prose_ids", R.domain == "prose_ids")):
        g = R[m].groupby(["policy", "budget"])[["nllA", "nllF", "nllG", "nll_indep", "n"]].sum()
        g["R_e2e"] = (g.nllA - g.nllG) / (g.nllA - g.nllF) * 100
        g["R_indep"] = (g.nllA - g.nll_indep) / (g.nllA - g.nllF) * 100
        piv = g.R_e2e.unstack("budget").round(1)
        piv.columns = [f"e2e@{int(100*c)}%" for c in piv.columns]
        piv2 = g.R_indep.unstack("budget").round(1)
        piv2.columns = [f"indep@{int(100*c)}%" for c in piv2.columns]
        gap = (g.nllA - g.nllF).iloc[0] / g.n.iloc[0]
        out.append(f"\n### {tag} — {pool}: % of local→full loss gap recovered (gap = {gap:.3f} nats/token)\n")
        out.append(pd.concat([piv, piv2], axis=1).to_markdown())
    (RES / f"e2e_{tag}.md").write_text("\n".join(out) + "\n")
    print("\n".join(out)); print(f"done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
