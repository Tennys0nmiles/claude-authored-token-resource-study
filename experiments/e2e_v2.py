"""End-to-end gated attention, version 2 (GPU).

Same protocol as e2e_gating.py: a frozen model, where every query attends to a local window of W keys plus the
first token and a gated query attends to the whole prefix; the gate is decided from an all-local pass. New:
  * several train/test document splits in one run (policies that need no training are evaluated once per document);
  * chunked scoring (no full-vocabulary log-softmax over the whole sequence), so 7B models fit at 8k tokens;
  * ridge heads fitted from streaming normal equations in float64 on the GPU. This is the same estimator as
    standardise-then-sklearn-Ridge, without holding every document's hidden states in memory at once;
  * optional "which vs whether" conditions (--blocks, first split only): per-head top-k block selection over the
    far region at a given far-key budget rho (an idealised Quest-style selector using exact block maxima), for every
    query ("block") or only for gated queries ("gate+block"); plus the plain gate run through the same custom
    attention path, to validate it against the SDPA-mask result.
Usage:
  python e2e_v2.py --model EleutherAI/pythia-160m-deduped --W 64 --T 1024 --splits 0,1,2,3,4
  python e2e_v2.py --model Qwen/Qwen2.5-7B --W 1024 --T 8192 --docs data/docs_long.jsonl --splits 0 --dtype bf16 --blocks
"""
import argparse, json, os, pathlib, random, time, types, zlib
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--W", type=int, required=True)
ap.add_argument("--T", type=int, default=1024)
ap.add_argument("--docs", default="data/docs.jsonl")
ap.add_argument("--splits", default="0")
ap.add_argument("--dtype", default="fp32", choices=["fp32", "bf16"])
ap.add_argument("--batch", type=int, default=4, help="gated masks per forward pass")
ap.add_argument("--blocks", action="store_true")
ap.add_argument("--block-size", type=int, default=16, help="keys per block (Quest's page size is 16)")
ap.add_argument("--head-chunk", type=int, default=4)
ap.add_argument("--limit", type=int, default=0, help="smoke test: first N documents per domain")
ap.add_argument("--conds", default="default", choices=["default", "recur", "all"], help="block-selection conditions")
ap.add_argument("--skip-pass2", action="store_true", help="skip the gated passes (e.g. when adding block conditions)")
ap.add_argument("--pass1-only", action="store_true", help="save per-token local/full values for every document and stop")
ap.add_argument("--recur-R", type=int, default=4, help="most recent earlier occurrences addressed per query")
ap.add_argument("--out", default="results/e2e_v2")
ap.add_argument("--scratch", default="/workspace/scratch")
args = ap.parse_args()

ROOT = pathlib.Path(__file__).parent
DEV = torch.device("cuda")
W, T, S_BLK = args.W, args.T, args.block_size
SPLITS = [int(s) for s in args.splits.split(",")]
BUDGETS = [0.05, 0.10, 0.20, 0.30]
TAG = f"{args.model.split('/')[-1]}_T{T}_W{W}" + (f"_lim{args.limit}" if args.limit else "")
OUT = pathlib.Path(args.out); OUT.mkdir(parents=True, exist_ok=True)
SCR = pathlib.Path(args.scratch) / TAG; SCR.mkdir(parents=True, exist_ok=True)
CSV, CSV_B = OUT / f"e2e2_{TAG}.csv", OUT / f"e2e2_{TAG}_blocks.csv"
t0 = time.time()


def log(*a):
    print(f"[{(time.time() - t0) / 60:6.1f} min]", *a, flush=True)


# ---------------- documents, identifier injection, splits, familiarity: as in collect.py / e2e_gating.py
src = (ROOT / "collect.py").read_text()
C = types.ModuleType("c"); C.__file__ = str(ROOT / "collect.py")
exec(src[: src.index("tok = AutoTokenizer")] + src[src.index("def clean(text):"): src.index("def _stats(")], C.__dict__)


def jobs():
    docs = [json.loads(l) for l in open(ROOT / args.docs)]
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
    """6 familiarity numbers per target index t (context ends at ids[t]); the earlier region excludes the
    local window: positions < t-W+1."""
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


# ---------------- model
dt = torch.float32 if args.dtype == "fp32" else torch.bfloat16
tok = AutoTokenizer.from_pretrained(args.model)
M = AutoModelForCausalLM.from_pretrained(args.model, dtype=dt, attn_implementation="sdpa").eval().to(DEV)
BASE = M.base_model
_head = M.get_output_embeddings()
HEAD_W = _head.weight.float()                        # fp32 unembedding (a copy for bf16 models)
HEAD_B = None if getattr(_head, "bias", None) is None else _head.bias.float()
BOS = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
NL = M.config.num_hidden_layers
FEAT_LAYERS = (NL // 2, NL)
V = HEAD_W.shape[0]


def chunk(B):
    return max(64, int(1.2e9 / (B * V * 4)))


def masks(n, gated_rows):
    i = torch.arange(n, device=DEV)[:, None]; j = torch.arange(n, device=DEV)[None, :]
    causal = j <= i
    local = causal & ((i - j < W) | (j == 0))
    return torch.stack([torch.where(torch.as_tensor(g, device=DEV)[:, None], causal, local)
                        for g in gated_rows])[:, None]


@torch.inference_mode()
def forward(ids_t, mask, want_hidden=False):
    x = ids_t[None].expand(mask.shape[0], -1)
    o = BASE(input_ids=x, attention_mask=mask, output_hidden_states=want_hidden, use_cache=False)
    return o.last_hidden_state, (o.hidden_states if want_hidden else None)


@torch.inference_mode()
def nll_of(last, y):
    """Per-target NLL [B, n-1] from final hidden states [B, n, d], computed in fp32 chunks."""
    B, n = last.shape[0], last.shape[1]
    out = torch.empty(B, n - 1, device=DEV)
    CH = chunk(B)
    for a in range(0, n - 1, CH):
        b = min(n - 1, a + CH)
        z = F.linear(last[:, a:b].float(), HEAD_W, HEAD_B)
        out[:, a:b] = torch.logsumexp(z, -1) - z.gather(-1, y[a:b][None, :, None].expand(B, -1, 1))[..., 0]
    return out


@torch.inference_mode()
def run_nll(ids_t, mask):
    res = []
    for s in range(0, mask.shape[0], args.batch):
        last, _ = forward(ids_t, mask[s:s + args.batch])
        res.append(nll_of(last, ids_t[1:]).cpu().numpy())
    return np.concatenate(res)


@torch.inference_mode()
def pass1(ids):
    """Local and full passes: per-target losses, local entropy, KL(full || local), local-pass features."""
    n = len(ids); ids_t = torch.tensor(ids, device=DEV)
    last, hs = forward(ids_t, masks(n, [np.zeros(n, bool), np.ones(n, bool)]), want_hidden=True)
    feats = torch.cat([hs[l][0, :-1] for l in FEAT_LAYERS], -1).to(torch.float16).cpu().numpy()
    del hs
    y = ids_t[1:]
    r = {k: torch.empty(n - 1, device=DEV) for k in ("nllA", "nllF", "HA", "KL")}
    CH = chunk(2)
    for a in range(0, n - 1, CH):
        b = min(n - 1, a + CH)
        lp = F.linear(last[:, a:b].float(), HEAD_W, HEAD_B).log_softmax(-1)
        lpA, lpF = lp[0], lp[1]
        yy = y[a:b, None]
        r["nllA"][a:b] = -lpA.gather(1, yy)[:, 0]; r["nllF"][a:b] = -lpF.gather(1, yy)[:, 0]
        r["HA"][a:b] = -(lpA.exp() * lpA).sum(-1)
        r["KL"][a:b] = (lpF.exp() * (lpF - lpA)).sum(-1)
        del lp, lpA, lpF
    rec = {k: v.cpu().numpy() for k, v in r.items()}
    rec.update(n=n, ids=ids, fam=familiarity(ids))
    return rec, feats


# ---------------- ridge from streaming normal equations (exactly: standardise with training mean/sd, then ridge)
class NormalEq:
    def __init__(self, D):
        z = lambda *s: torch.zeros(*s, dtype=torch.float64, device=DEV)
        self.S, self.s1, self.sy, self.n, self.ysum = z(D, D), z(D), z(D), 0, 0.0

    def add(self, X, y):
        X, y = X.double(), y.double()
        self.S += X.T @ X; self.s1 += X.sum(0); self.sy += X.T @ y
        self.n += X.shape[0]; self.ysum += float(y.sum())

    def fit(self, cols, alpha):
        c = torch.as_tensor(cols, device=DEV); n = self.n
        mu = self.s1[c] / n; ybar = self.ysum / n
        Cm = self.S[c][:, c] / n - torch.outer(mu, mu)
        sd = torch.sqrt(torch.clamp(torch.diag(Cm), min=0)) + 1e-6
        A = n * Cm / torch.outer(sd, sd) + alpha * torch.eye(len(cols), dtype=torch.float64, device=DEV)
        w = torch.linalg.solve(A, (self.sy[c] - n * mu * ybar) / sd)
        return c, mu, sd, w


def design(rec, feats, idx):
    X = torch.from_numpy(feats[idx]).to(DEV).float()
    return torch.cat([X, torch.from_numpy(rec["HA"][idx, None]).to(DEV),
                      torch.from_numpy(rec["fam"][idx]).to(DEV)], 1)


def predict(head, X):
    c, mu, sd, w = head
    return (((X[:, c].double() - mu) / sd) @ w).cpu().numpy()


# ---------------- custom attention for the block-selection conditions (routes to SDPA unless CTX["on"])
CTX = {"on": False}
_orig_sdpa = ALL_ATTENTION_FUNCTIONS["sdpa"]


def routed_attention(module, query, key, value, attention_mask, dropout=0.0, scaling=None, **kw):
    if not CTX["on"]:
        return _orig_sdpa(module, query, key, value, attention_mask, dropout=dropout, scaling=scaling, **kw)
    B, H, n, d = query.shape
    rep = H // key.shape[1]
    scale = scaling if scaling is not None else d ** -0.5
    i = torch.arange(n, device=query.device)[:, None]; j = torch.arange(n, device=query.device)[None, :]
    causal = j <= i; local = causal & ((i - j < W) | (j == 0)); far = causal & ~local
    nfar = far.sum(-1)
    nb = (n + S_BLK - 1) // S_BLK
    out = torch.empty(B, n, H, d, dtype=query.dtype, device=query.device)
    for bi in range(B):
        it = CTX["items"][bi]
        gated, rho = it["gated"], it["rho"]
        for h0 in range(0, H, args.head_chunk):
            h1 = min(H, h0 + args.head_chunk)
            kv_idx = torch.arange(h0, h1, device=query.device) // rep
            q = query[bi, h0:h1].float()
            k = key[bi, kv_idx].float()
            sc = torch.matmul(q, k.transpose(-1, -2)) * scale                      # [h, n, n]
            if rho is None:                                                         # plain per-query gate
                allowed = (local | (far & gated[:, None]))[None]
            elif it["scorer"] == "recur":                                           # recurrence-addressed blocks only
                selb = it["rec"][None].expand(h1 - h0, n, nb).clone()
                if gated is not None:
                    selb &= gated[None, :, None]
                sel = selb.repeat_interleave(S_BLK, -1)[..., :n] & far[None]
                if getattr(module, "layer_idx", None) == 0:
                    it["far_read"] += float(sel[:, W - 1:n - 1].sum()) / H
                allowed = local[None] | sel
            else:                                                                   # top-k far blocks per head
                if it["scorer"] == "exact":                                         # exact block maxima (upper bound)
                    sf = sc.masked_fill(~far, float("-inf"))
                    if nb * S_BLK > n:
                        sf = F.pad(sf, (0, nb * S_BLK - n), value=float("-inf"))
                    bmax = sf.view(h1 - h0, n, nb, S_BLK).amax(-1)                 # [h, n, nb]
                    del sf
                else:                                                               # Quest-style bound from per-block
                    kp = F.pad(k, (0, 0, 0, nb * S_BLK - n)).view(h1 - h0, nb, S_BLK, d)   # key min/max
                    real = (torch.arange(nb * S_BLK, device=query.device) < n).view(nb, S_BLK)[None, :, :, None]
                    kmax = kp.masked_fill(~real, float("-inf")).amax(2)
                    kmin = kp.masked_fill(~real, float("inf")).amin(2)
                    bmax = (torch.matmul(q.clamp(min=0), kmax.transpose(-1, -2)) +
                            torch.matmul(q.clamp(max=0), kmin.transpose(-1, -2))) * scale
                    bstart = (torch.arange(nb, device=query.device) * S_BLK).clamp(min=1)
                    has_far = bstart[None, :] <= (torch.arange(n, device=query.device) - W)[:, None]
                    bmax = bmax.masked_fill(~has_far[None], float("-inf"))
                kq = torch.ceil(rho * nfar.float() / S_BLK).long()
                rank = bmax.argsort(-1, descending=True).argsort(-1)
                selb = (rank < kq[None, :, None]) & torch.isfinite(bmax)
                if it["scorer"] == "recur+quest":                                   # union with recurrence blocks
                    selb |= it["rec"][None]
                if gated is not None:
                    selb &= gated[None, :, None]
                sel = selb.repeat_interleave(S_BLK, -1)[..., :n] & far[None]
                if getattr(module, "layer_idx", None) == 0:
                    it["far_read"] += float(sel[:, W - 1:n - 1].sum()) / H
                allowed = local[None] | sel
            p = sc.masked_fill(~allowed, float("-inf")).softmax(-1)
            vv = value[bi, kv_idx]
            out[bi, :, h0:h1] = torch.matmul(p.to(vv.dtype), vv).transpose(0, 1)
            del sc, p, allowed
    return out, None


ALL_ATTENTION_FUNCTIONS["sdpa"] = routed_attention


def recurrence_blocks(ids, nb, R=4, mmax=4, mmin=2):
    """For each query i: find the longest n-gram (mmax..mmin tokens) ending at i that occurred earlier entirely in the
    far region (ending at p <= i-W-1); address the key blocks holding its continuation (positions p+1 and p+9) for the
    R most recent occurrences. Hash lookups only: no keys are read to decide. Returns a bool [n, nb] block mask."""
    n = len(ids)
    occ = {m: {} for m in range(mmin, mmax + 1)}
    rows, cols = [], []
    added = 0
    for i in range(n):
        while added <= i - W - 1:                        # n-grams ending at position `added` become addressable
            p = added
            for m in range(mmin, mmax + 1):
                if p - m + 1 >= 0:
                    occ[m].setdefault(tuple(ids[p - m + 1:p + 1]), []).append(p)
            added += 1
        for m in range(mmax, mmin - 1, -1):
            if i - m + 1 < 0:
                continue
            lst = occ[m].get(tuple(ids[i - m + 1:i + 1]))
            if lst:
                for p in lst[-R:]:
                    for q in (p + 1, p + 9):
                        if 1 <= q <= i - W:
                            rows.append(i); cols.append(q // S_BLK)
                break
    mask = np.zeros((n, nb), bool)
    if rows:
        mask[rows, cols] = True
    return mask


# ---------------- main
VALID = {}                                             # doc -> gated nll (learned head, 10%, first split), for checks


def gate_sets(n, idx, s):
    order = np.argsort(-s, kind="stable")
    sets = []
    for b in BUDGETS:
        g = np.zeros(n, bool); g[idx[order[: int(round(b * len(idx)))]]] = True; sets.append(g)
    return sets


def main():
    J = jobs()
    trains = {s: split_docs(J, s) for s in SPLITS}
    if args.limit:                                   # smoke test: N training and N test documents per domain
        keep = set()
        for dom in ("prose", "code"):
            ids_ = sorted(j[0] for j in J if j[1] == dom)
            keep |= set([d for d in ids_ if d in trains[SPLITS[0]]][: args.limit])
            keep |= set([d for d in ids_ if d not in trains[SPLITS[0]]][: args.limit])
        J = [j for j in J if j[0].replace("+ids", "") in keep]
    base = lambda did: did.replace("+ids", "")
    natural = lambda dom: dom in ("prose", "code")
    test_of = {j[0]: [s for s in SPLITS if base(j[0]) not in trains[s]] for j in J}
    need = [j for j in J if test_of[j[0]] or (natural(j[1]) and any(base(j[0]) in trains[s] for s in SPLITS))]
    if args.pass1_only:
        need = J
    log(f"{args.model} T={T} W={W} dtype={args.dtype} splits={SPLITS}: {len(need)} documents")

    # pass 1 (split-independent)
    recs = {}
    for k, (did, dom, text, _) in enumerate(need):
        ids = [BOS] + tok(text, add_special_tokens=False)["input_ids"][:T]
        if len(ids) < 256:
            continue
        rec, feats = pass1(ids)
        rec["dom"] = dom
        fp = SCR / (did.replace("/", "__") + ".npy"); np.save(fp, feats); rec["feats"] = fp
        recs[did] = rec
        if k % 20 == 0:
            log(f"pass1 {k + 1}/{len(need)}")
    if args.pass1_only:                                  # per-token values for the cross-resource atlas
        tok_rows = []
        for did, r in recs.items():
            m = r["n"] - 1
            tok_rows.append(pd.DataFrame(dict(doc=did, domain=r["dom"], pos=np.arange(1, m + 1), tok=np.asarray(r["ids"][1:]),
                                              nllA=r["nllA"], nllF=r["nllF"], HA=r["HA"], KL=r["KL"], fam4=r["fam"][:, 2] > 0)))
        pd.concat(tok_rows).to_parquet(OUT / f"tokens_{TAG}.parquet")
        log(f"saved per-token values for {len(recs)} documents"); return
    D = 2 * M.config.hidden_size + 7
    dH = 2 * M.config.hidden_size

    # heads per split, and learned scores for that split's test documents
    learned = {}
    for s in SPLITS:
        ne = NormalEq(D)
        for did, r in recs.items():
            if natural(r["dom"]) and base(did) in trains[s]:
                idx = np.arange(W - 1, r["n"] - 1)
                ne.add(design(r, np.load(r["feats"], mmap_mode="r"), idx), torch.from_numpy(r["KL"][idx]).to(DEV))
        heads = {"learned": ne.fit(list(range(D)), 1000.0),
                 "hidden_only": ne.fit(list(range(dH + 1)), 1000.0),
                 "fam_head": ne.fit(list(range(dH, D)), 10.0)}
        for did, r in recs.items():
            if s in test_of[did]:
                idx = np.arange(W - 1, r["n"] - 1)
                X = design(r, np.load(r["feats"], mmap_mode="r"), idx)
                learned[(did, s)] = {p: predict(h, X) for p, h in heads.items()}
        log(f"split {s}: heads fitted on {ne.n} tokens")

    # pass 2: gated forward passes
    done = set()
    if CSV.exists():
        old = pd.read_csv(CSV)
        done = set(zip(old.split, old.doc, old.policy))
    fixed = ["random", "entropy", "fam_rule", "oracle"]
    for k, (did, r) in enumerate(recs.items()):
        if not test_of[did] or args.skip_pass2:
            continue
        n = r["n"]; idx = np.arange(W - 1, n - 1); ids_t = torch.tensor(r["ids"], device=DEV)
        nfar = np.maximum(0, np.arange(n) - W)[idx].astype(np.float64)
        fam = r["fam"][idx]
        rng = np.random.default_rng(zlib.crc32(did.encode()))
        scores = {"random": rng.random(len(idx)), "entropy": r["HA"][idx],
                  "fam_rule": 4 * fam[:, 2] + 2 * fam[:, 1] + fam[:, 0] + 0.01 * r["HA"][idx],
                  "oracle": r["KL"][idx]}
        todo = [(p, None) for p in fixed] + [(p, s) for s in test_of[did] for p in ("fam_head", "hidden_only", "learned")]
        rows = []
        for p, s in todo:
            splits_here = test_of[did] if s is None else [s]
            if all((sp, did, p) in done for sp in splits_here):
                continue
            sc = scores[p] if s is None else learned[(did, s)][p]
            sets = gate_sets(n, idx, sc)
            nll = run_nll(ids_t, masks(n, sets))
            for bi, b in enumerate(BUDGETS):
                if p == "learned" and s == SPLITS[0] and b == 0.10:
                    VALID[did] = float(nll[bi][idx].sum())
                g = sets[bi][:n - 1]
                indep = r["nllA"][idx].sum() - (r["nllA"][idx] - r["nllF"][idx])[g[idx]].sum()
                far_frac = nfar[g[idx]].sum() / nfar.sum()
                for sp in splits_here:
                    rows.append(dict(split=sp, doc=did, domain=r["dom"], n=len(idx), nllA=float(r["nllA"][idx].sum()),
                                     nllF=float(r["nllF"][idx].sum()), policy=p, budget=b,
                                     nllG=float(nll[bi][idx].sum()), nll_indep=float(indep), far_frac=float(far_frac)))
        if rows:
            pd.DataFrame(rows).to_csv(CSV, mode="a", header=not CSV.exists(), index=False)
        if k % 10 == 0:
            log(f"pass2 {k + 1}/{len(recs)}")

    # which vs whether (first split only)
    if args.blocks:
        s0 = SPLITS[0]
        # (condition, gate policy, gate budget, far-key fraction rho for gated/eligible queries, block scorer)
        default = [("block", None, None, rho, sc_) for sc_ in ("exact", "quest") for rho in (0.025, 0.05, 0.10, 0.20)] + \
                  [("gate+block", p, b, rho, "quest") for p in ("learned", "entropy") for b, rho in ((0.20, 0.50), (0.30, 1 / 3))] + \
                  [("gate", "learned", 0.10, None, "")]
        recur = [("recur", None, None, 0.0, "recur"), ("recur+quest", None, None, 0.025, "recur+quest"),
                 ("recur+quest", None, None, 0.05, "recur+quest"), ("block", None, None, 0.005, "quest"),
                 ("block", None, None, 0.01, "quest"), ("block", None, None, 0.01, "exact")]
        conds = {"default": default, "recur": recur, "all": default + recur}[args.conds]
        global CSV_B
        if args.conds == "recur":
            CSV_B = OUT / f"e2e2_{TAG}_blocks_recur.csv"
        doneb = set(pd.read_csv(CSV_B).doc) if CSV_B.exists() else set()
        for k, (did, r) in enumerate(recs.items()):
            if s0 not in test_of[did] or did in doneb:
                continue
            n = r["n"]; idx = np.arange(W - 1, n - 1); ids_t = torch.tensor(r["ids"], device=DEV)
            nfar = np.maximum(0, np.arange(n) - W)[idx].astype(np.float64)
            sc = {"learned": learned[(did, s0)]["learned"], "entropy": r["HA"][idx]}
            nb_ = (n + S_BLK - 1) // S_BLK
            rec = torch.as_tensor(recurrence_blocks(r["ids"], nb_, R=args.recur_R), device=DEV) \
                if any(c[4] in ("recur", "recur+quest") for c in conds) else None
            rows = []
            for c0 in range(0, len(conds), args.batch):
                items, cc = [], conds[c0:c0 + args.batch]
                for mode, p, b, rho, scorer in cc:
                    g = None
                    if p is not None:                  # same top-b rule as gate_sets()
                        order = np.argsort(-sc[p], kind="stable"); g = np.zeros(n, bool)
                        g[idx[order[: int(round(b * len(idx)))]]] = True
                        g = torch.as_tensor(g, device=DEV)
                    items.append(dict(gated=g, rho=rho, scorer=scorer, far_read=0.0, rec=rec))
                CTX.update(on=True, items=items)
                try:
                    nll = run_nll_blocks(ids_t, len(items))
                finally:
                    CTX["on"] = False
                for (mode, p, b, rho, scorer), it, nl in zip(cc, items, nll):
                    if rho is None:
                        far = nfar[it["gated"].cpu().numpy()[idx]].sum()
                    else:
                        far = it["far_read"]
                    touch = 1.0 if it["gated"] is None else float(it["gated"].cpu().numpy()[idx].mean())
                    if scorer == "recur":                  # queries that address any far block
                        touch = float(rec[W - 1:n - 1].any(-1).float().mean())
                    rows.append(dict(split=s0, doc=did, domain=r["dom"], n=len(idx), nllA=float(r["nllA"][idx].sum()),
                                     nllF=float(r["nllF"][idx].sum()), cond=mode, scorer=scorer, gate_policy=p or "",
                                     b=b if b is not None else np.nan, rho=rho if rho is not None else np.nan,
                                     nllG=float(nl[idx].sum()), far_frac=float(far / nfar.sum()), touch_frac=touch))
            ref = VALID.get(did)                       # plain gate through the custom path vs the SDPA-mask pass
            if ref is not None and any(x["cond"] == "gate" for x in rows):
                mine = [x["nllG"] for x in rows if x["cond"] == "gate"][0]
                log(f"validation {did}: custom-path gate nll {mine:.4f} vs SDPA-mask {ref:.4f} "
                    f"(rel diff {abs(mine - ref) / abs(ref):.2e})")
            pd.DataFrame(rows).to_csv(CSV_B, mode="a", header=not CSV_B.exists(), index=False)
            if k % 10 == 0:
                log(f"blocks {k + 1}/{len(recs)}")
    json.dump(dict(vars(args), tag=TAG, n_docs=len(recs), minutes=(time.time() - t0) / 60,
                   tokens={d: int(r["n"]) for d, r in recs.items()}), open(OUT / f"e2e2_{TAG}_meta.json", "w"), indent=1)
    log("done")


@torch.inference_mode()
def run_nll_blocks(ids_t, B):
    n = ids_t.shape[0]
    mask = masks(n, [np.zeros(n, bool)] * B)            # ignored by the custom attention path
    last, _ = forward(ids_t, mask)
    return nll_of(last, ids_t[1:]).cpu().numpy()


if __name__ == "__main__":
    main()
