"""Per-token measurement of *where extra resources actually help* in natural text.

For every token we record, from a cheap model S and an expensive model L (same tokenizer,
same training data -- the Pythia suite):

  H_S        entropy of S's next-token distribution            (the usual "surprise" signal)
  nll_S      S's loss with full document context
  nll_L      L's loss with full document context
  nll_Ss     S's loss with only 32-63 tokens of local context
  gain_c   = nll_S  - nll_L    realized benefit of more COMPUTE (bigger model)
  gain_m   = nll_Ss - nll_S    realized benefit of more MEMORY  (long context)
  KL_LS    = KL(p_L || p_S)     expected compute benefit if L were the truth (smooth target)
  KL_SSs   = KL(p_S || p_Ss)    expected memory benefit, same idea

plus cheap features computable from S alone (hidden states, logit-lens entropy), which a
learned "value-of-resource" head can use.

A third document set injects random hex identifiers into the prose documents: some appear
once (irreducible by any resource), some appear twice (reducible by memory, not by compute).
"""
import json, math, random, re, sys, time, pathlib, os
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

ROOT = pathlib.Path(__file__).parent
S_NAME = os.environ.get("S_NAME", "EleutherAI/pythia-160m-deduped")
L_NAME = sys.argv[1] if len(sys.argv) > 1 else "EleutherAI/pythia-1.4b-deduped"
T = int(os.environ.get("T_TOK", "1024"))  # tokens per document (after a BOS token)
WIN, STRIDE = 64, 32
FEAT_LAYERS = (6, 12)   # S hidden-state layers kept as features
torch.set_num_threads(10)
DEV = torch.device(os.environ.get('DEV', 'cuda' if torch.cuda.is_available() else 'cpu'))
RES = pathlib.Path(os.environ.get('PILOT_RES', ROOT / 'results')); RES.mkdir(parents=True, exist_ok=True)
DOCS = pathlib.Path(os.environ.get('DOCS', ROOT / 'data' / 'docs.jsonl'))
torch.manual_seed(0)

tok = AutoTokenizer.from_pretrained(S_NAME)
S = AutoModelForCausalLM.from_pretrained(S_NAME, dtype=torch.float32).eval().to(DEV)
L = AutoModelForCausalLM.from_pretrained(L_NAME, dtype=torch.float32).eval().to(DEV)
FEAT_LAYERS = (S.config.num_hidden_layers // 2, S.config.num_hidden_layers)   # middle + last
VC = min(S.config.vocab_size, L.config.vocab_size, len(tok))   # real tokens only (Pythia pads to 50304/50432)
EXCL = [tok.eos_token_id]   # <|endoftext|> never occurs inside our documents; some models (e.g. Pythia-2.8B) put
                            # large mass on it after blank lines, which dominated KL(p_L||p_S) with 300-500 nat
                            # outliers. Distributions are compared over tokens that can occur in the text.


def real_logits(z):
    z = z[..., :VC].float()
    z[..., EXCL] = -1e4        # finite: exp() underflows to exactly 0, and 0 * log p stays 0 (no NaN)
    return z
BOS = tok.eos_token_id  # Pythia uses <|endoftext|> (id 0) as document separator


def clean(text):
    text = text.replace("Content selection saved. Describe the issue below:", "")
    return text.strip()


def inject_ids(text, rng):
    """Insert 10 bracketed 8-hex identifiers at sentence ends in the first ~3500 chars.
    6 are one-off, 2 are inserted twice (second copy >= 3 insertion slots later)."""
    cut = [m.end() for m in re.finditer(r"\.\s", text[:3500])]
    if len(cut) < 12:
        return None, []
    slots = sorted(rng.sample(cut, 12))
    ids = ["".join(rng.choice("0123456789abcdef") for _ in range(8)) for _ in range(8)]
    plan = [None] * 12
    # two repeated ids: first at slots a, second at slot a+k (k>=3)
    rep_first = rng.sample(range(0, 6), 2)
    used = set()
    for j, a in enumerate(rep_first):
        b = min(11, a + 3 + rng.randrange(3))
        while b in used or b == a or plan[b] is not None:
            b = (b + 1) % 12
        plan[a], plan[b] = (ids[j], "id_first"), (ids[j], "id_repeat")
        used |= {a, b}
    k = 2
    for s in range(12):
        if plan[s] is None and k < 8:
            plan[s] = (ids[k], "id_first"); k += 1
    out, spans, prev = [], [], 0
    for s, p in zip(slots, plan):
        if p is None:
            continue
        out.append(text[prev:s])
        pre = " [ref "
        start = sum(len(x) for x in out) + len(pre)
        out.append(pre + p[0] + "] ")
        spans.append((start, start + len(p[0]), p[1]))
        prev = s
    out.append(text[prev:])
    return "".join(out), spans


def _stats(lp_a, lp_b):
    """entropy of a, KL(a||b), for row-chunks of log-prob matrices."""
    pa = lp_a.exp()
    return -(pa * lp_a).sum(-1), (pa * (lp_a - lp_b)).sum(-1)


@torch.inference_mode()
def measure(ids, CH=256):
    """ids: LongTensor [n] starting with BOS. Returns dict of per-target arrays (n-1).
    Vocabulary-sized tensors are processed in row chunks of CH to bound memory."""
    ids = ids.to(DEV)
    n = ids.shape[0]
    x = ids[None]
    y = ids[1:]
    oS = S(x, output_hidden_states=True)
    lpS = F.log_softmax(real_logits(oS.logits[0, :-1]), -1)             # [n-1, V]
    del oS.logits
    E = lambda: torch.empty(n - 1, device=DEV)
    H_S = E(); pmax_S = E()
    H_S6 = E(); KL_S_S6 = E()
    h6 = oS.hidden_states[FEAT_LAYERS[0]][0, :-1]   # logit lens at the middle layer
    for a in range(0, n - 1, CH):
        b = min(n - 1, a + CH)
        lp6 = F.log_softmax(real_logits(S.get_output_embeddings()(S.gpt_neox.final_layer_norm(h6[a:b]))), -1)
        H_S[a:b], KL_S_S6[a:b] = _stats(lpS[a:b], lp6)
        H_S6[a:b] = -(lp6.exp() * lp6).sum(-1)
        pmax_S[a:b] = lpS[a:b].max(-1).values.exp()
    nll_S = -lpS.gather(1, y[:, None])[:, 0]
    feats = torch.cat([oS.hidden_states[l][0, :-1] for l in FEAT_LAYERS], -1).to(torch.float16)
    del oS
    # expensive model, full context
    logitsL = real_logits(L(x).logits[0, :-1])
    H_L = E(); KL_LS = E(); nll_L = E()
    for a in range(0, n - 1, CH):
        b = min(n - 1, a + CH)
        lpL = F.log_softmax(logitsL[a:b].float(), -1)
        H_L[a:b], KL_LS[a:b] = _stats(lpL, lpS[a:b])
        nll_L[a:b] = -lpL.gather(1, y[a:b, None])[:, 0]
    del logitsL
    # short-context S: windows of WIN tokens, stride STRIDE; each target sees 32..63 tokens
    starts = list(range(0, max(1, n - WIN) + 1, STRIDE))
    if starts[-1] + WIN < n:
        starts.append(n - WIN)
    nll_Ss = torch.full((n - 1,), float("nan"), device=DEV); H_Ss = nll_Ss.clone(); KL_SSs = nll_Ss.clone()
    filled_h = np.zeros(n - 1, bool)
    for w0 in range(0, len(starts), 8):
        grp = starts[w0:w0 + 8]
        lw = real_logits(S(torch.stack([ids[s:s + WIN] for s in grp])).logits[:, :-1])
        for g, s in enumerate(grp):
            lo = 0 if s == 0 else STRIDE - 1
            ts = [s + j for j in range(lo, WIN - 1) if s + j < n - 1 and not filled_h[s + j]]
            filled_h[ts] = True
            if not ts:
                continue
            js = torch.tensor([t - s for t in ts], device=DEV); ts = torch.tensor(ts, device=DEV)
            lps = F.log_softmax(lw[g, js].float(), -1)
            nll_Ss[ts] = -lps.gather(1, y[ts, None])[:, 0]
            H_Ss[ts] = -(lps.exp() * lps).sum(-1)
            KL_SSs[ts] = (lpS[ts].exp() * (lpS[ts] - lps)).sum(-1)
        del lw
    assert not torch.isnan(nll_Ss).any()
    out = dict(H_S=H_S, H_L=H_L, nll_S=nll_S, nll_L=nll_L, KL_LS=KL_LS, pmax_S=pmax_S,
               H_S6=H_S6, KL_S_S6=KL_S_S6, nll_Ss=nll_Ss, H_Ss=H_Ss, KL_SSs=KL_SSs)
    out = {k: v.float().cpu().numpy() for k, v in out.items()}
    out["feats"] = feats.cpu().numpy()
    out["tok"] = y.cpu().numpy()
    return out


def main():
    docs = [json.loads(l) for l in open(DOCS)]
    rng = random.Random(1)
    jobs = []
    for d in docs:
        jobs.append((d["id"], d["domain"], clean(d["text"]), []))
    for d in docs:
        if d["domain"] == "prose":
            txt, spans = inject_ids(clean(d["text"]), rng)
            if txt:
                jobs.append((d["id"] + "+ids", "prose_ids", txt, spans))
    import os
    lim = int(os.environ.get("LIMIT", "0"))
    if lim:  # smoke test: a few plain docs and a few id-injected docs
        jobs = jobs[:lim] + jobs[-lim:]
    rows, n_docs, row0 = [], 0, 0
    D = S.config.hidden_size * len(FEAT_LAYERS)
    fmap = np.lib.format.open_memmap(RES / "feats_S.npy", mode="w+",
                                     dtype=np.float16, shape=(len(jobs) * T, D))
    t0 = time.time()
    for i, (did, dom, text, spans) in enumerate(jobs):
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        ids = [BOS] + enc["input_ids"][: T]
        offs = [(-1, -1)] + enc["offset_mapping"][: T]
        if len(ids) < 256:
            continue
        m = measure(torch.tensor(ids))
        n = len(ids) - 1
        label = np.array(["natural"] * n, dtype=object)
        for (a, b, lab) in spans:
            for t in range(n):
                s0, s1 = offs[t + 1]
                if s0 < b and s1 > a:
                    label[t] = lab
        for t in range(n):
            rows.append((i, did, dom, t + 1, int(m["tok"][t]), label[t],
                         *[float(m[k][t]) for k in ("H_S", "H_L", "nll_S", "nll_L", "KL_LS", "pmax_S",
                                                    "H_S6", "KL_S_S6", "nll_Ss", "H_Ss", "KL_SSs")]))
        fmap[row0:row0 + n] = m["feats"]; row0 += n; n_docs += 1
        el = time.time() - t0
        print(f"[{i+1}/{len(jobs)}] {dom:9s} {did[:40]:40s} n={n} "
              f"nllS={m['nll_S'].mean():.3f} nllL={m['nll_L'].mean():.3f} "
              f"nllSs={m['nll_Ss'].mean():.3f}  {el/60:.1f} min", flush=True)
    cols = ["doc", "doc_id", "domain", "pos", "tok", "label", "H_S", "H_L", "nll_S", "nll_L",
            "KL_LS", "pmax_S", "H_S6", "KL_S_S6", "nll_Ss", "H_Ss", "KL_SSs"]
    import pandas as pd
    df = pd.DataFrame(rows, columns=cols)
    df.to_parquet(RES / "per_token.parquet") if _has_pyarrow() else \
        df.to_csv(RES / "per_token.csv.gz", index=False)
    fmap.flush(); del fmap
    np.save(RES / "feats_rows.npy", np.array([row0]))  # valid rows = first row0
    json.dump({"S": S_NAME, "L": L_NAME, "T": T, "win": WIN, "stride": STRIDE,
               "feat_layers": FEAT_LAYERS, "n_tokens": len(df), "n_docs": n_docs,
               "minutes": (time.time() - t0) / 60},
              open(RES / "collect_meta.json", "w"), indent=1)
    print("done", len(df), "tokens")


def _has_pyarrow():
    try:
        import pyarrow  # noqa
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    main()
