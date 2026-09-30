"""Internal-depth version of Experiment A (Spec 1a, CPU scale).

Resource = the upper half of ONE network. Pythia-1.4B (24 layers) gets tuned-lens early
exits (Belrose et al. 2023 style: h' = h + A h + b, then the model's own final LayerNorm and
unembedding) at layers 8, 12, 16, trained by KL to the final layer on separate 2026 text
(data/lens_docs.jsonl). For every evaluation token we then measure

  gain_d = nll(exit@12) - nll(final)        realized value of running layers 13-24
  KL_d   = KL(p_final || p_exit12)          smooth target

and ask which cheap signal, available AT the exit, predicts gain_d: the exit's entropy or
confidence (what early-exit methods such as CALM use), the change between exits 8 and 12
("saturation"), or a learned value head on the layer-12 hidden state.

Stages: python depth_lens.py acts | lenses | eval | analyze   (or: all)
"""
import json, sys, time, pathlib, random, types
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT = pathlib.Path(__file__).parent
import os
RES = pathlib.Path(os.environ.get("PILOT_RES", ROOT / "results")); RES.mkdir(parents=True, exist_ok=True)
SCR = pathlib.Path(os.environ.get("DEPTH_SCR", str(ROOT / "scratch" / "depth")))
SCR.mkdir(parents=True, exist_ok=True)
NAME = os.environ.get("DEPTH_MODEL", "EleutherAI/pythia-1.4b-deduped")
LAYERS = (8, 12, 16)
EXIT = 12
T = 1024
PROJ = 768
torch.set_num_threads(10)
DEV = torch.device(os.environ.get('DEV', 'cuda' if torch.cuda.is_available() else 'cpu'))
torch.manual_seed(0)


def load_model():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(NAME)
    M = AutoModelForCausalLM.from_pretrained(NAME, dtype=torch.float32).eval().to(DEV)
    return tok, M


def head_fns(M):
    ln = M.gpt_neox.final_layer_norm
    U = M.get_output_embeddings()
    return ln, U


def stage_acts():
    """Hidden states at LAYERS + final (post-LN) for lens-training docs -> fp16 memmaps."""
    tok, M = load_model()
    docs = [json.loads(l) for l in open(ROOT / "data" / "lens_docs.jsonl")]
    D = M.config.hidden_size
    maps = {l: np.lib.format.open_memmap(SCR / f"lens_h{l}.npy", "w+", np.float16, (len(docs) * T, D))
            for l in (*LAYERS, "final")}
    r = 0
    t0 = time.time()
    with torch.inference_mode():
        for k, d in enumerate(docs):
            ids = [tok.eos_token_id] + tok(d["text"], add_special_tokens=False)["input_ids"][:T]
            if len(ids) < 256:
                continue
            hs = M(torch.tensor([ids], device=DEV), output_hidden_states=True).hidden_states
            n = len(ids) - 1
            for l in LAYERS:
                maps[l][r:r + n] = hs[l][0, :-1].float().cpu().numpy()
            maps["final"][r:r + n] = hs[-1][0, :-1].float().cpu().numpy()
            r += n
            print(f"[acts {k+1}/{len(docs)}] {time.time()-t0:.0f}s", flush=True)
    for m in maps.values():
        m.flush()
    np.save(SCR / "lens_rows.npy", np.array([r]))


def check_last_hidden(M, ids):
    """Is hidden_states[-1] already post-final-LN? (decides how the target logits are formed)"""
    with torch.inference_mode():
        o = M(ids, output_hidden_states=True)
        ln, U = head_fns(M)
        a = (U(o.hidden_states[-1]) - o.logits).abs().max().item()
        b = (U(ln(o.hidden_states[-1])) - o.logits).abs().max().item()
    return a < b


def stage_lenses():
    tok, M = load_model()
    post_ln = check_last_hidden(M, torch.tensor([[0, 510, 1123, 247, 3565]], device=DEV))
    print("hidden_states[-1] is post-LN:", post_ln, flush=True)
    ln, U = head_fns(M)
    del M.gpt_neox.layers                                   # only the LayerNorm + unembedding are needed
    for p in list(ln.parameters()) + list(U.parameters()):
        p.requires_grad_(False)
    rows = int(np.load(SCR / "lens_rows.npy")[0])
    Hf = np.load(SCR / "lens_hfinal.npy", mmap_mode="r")
    for l in LAYERS:
        H = np.load(SCR / f"lens_h{l}.npy", mmap_mode="r")
        D = H.shape[1]
        lens = torch.nn.Linear(D, D).to(DEV)
        torch.nn.init.zeros_(lens.weight); torch.nn.init.zeros_(lens.bias)
        opt = torch.optim.Adam(lens.parameters(), lr=1e-3)
        B, EPOCHS = 512, 2
        order = np.arange(rows)
        t0 = time.time(); step = 0
        for ep in range(EPOCHS):
            np.random.default_rng(ep).shuffle(order)
            for s in range(0, rows - B + 1, B):
                ix = np.sort(order[s:s + B])
                h = torch.from_numpy(np.asarray(H[ix], dtype=np.float32)).to(DEV)
                hf = torch.from_numpy(np.asarray(Hf[ix], dtype=np.float32)).to(DEV)
                with torch.no_grad():
                    tgt = F.log_softmax(U(hf if post_ln else ln(hf)), -1)
                lp = F.log_softmax(U(ln(h + lens(h))), -1)
                loss = (tgt.exp() * (tgt - lp)).sum(-1).mean()
                opt.zero_grad(); loss.backward(); opt.step(); step += 1
                if step % 25 == 0:
                    print(f"[lens L{l}] ep{ep} step{step} KL={loss.item():.3f} {time.time()-t0:.0f}s", flush=True)
        torch.save({k: v.cpu() for k, v in lens.state_dict().items()}, SCR / f"lens_L{l}.pt")


def eval_jobs():
    src = (ROOT / "collect.py").read_text()
    C = types.ModuleType("c"); C.__file__ = str(ROOT / "collect.py")
    exec(src[: src.index("tok = AutoTokenizer")] + src[src.index("def clean(text):"): src.index("def _stats(")], C.__dict__)
    docs = [json.loads(l) for l in open(ROOT / "data" / "docs.jsonl")]
    rng = random.Random(1)
    out = [(d["id"], d["domain"], C.clean(d["text"]), []) for d in docs]
    for d in docs:
        if d["domain"] == "prose":
            txt, spans = C.inject_ids(C.clean(d["text"]), rng)
            if txt:
                out.append((d["id"] + "+ids", "prose_ids", txt, spans))
    return out


def stage_eval():
    tok, M = load_model()
    post_ln = check_last_hidden(M, torch.tensor([[0, 510, 1123, 247, 3565]], device=DEV))
    ln, U = head_fns(M)
    D = M.config.hidden_size
    lenses = {}
    for l in LAYERS:
        m = torch.nn.Linear(D, D); m.load_state_dict(torch.load(SCR / f"lens_L{l}.pt")); m.eval().to(DEV)
        lenses[l] = m
    g = torch.Generator().manual_seed(0)
    P = (torch.randn(D, PROJ, generator=g) / PROJ ** 0.5).to(DEV)          # fixed random projection
    J = eval_jobs()
    fmap = np.lib.format.open_memmap(RES / "feats_depth.npy", "w+", np.float16, (len(J) * T, PROJ))
    rows, r0, t0 = [], 0, time.time()
    with torch.inference_mode():
        for k, (did, dom, text, spans) in enumerate(J):
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
            ids = [tok.eos_token_id] + enc["input_ids"][:T]
            offs = [(-1, -1)] + enc["offset_mapping"][:T]
            if len(ids) < 256:
                continue
            x = torch.tensor([ids], device=DEV); y = x[0, 1:]; n = len(ids) - 1
            o = M(x, output_hidden_states=True)
            logits = o.logits[0, :-1]
            keys = ["nll_final", "H_final", "KL_12_8"] + [f"{a}_{l}" for l in LAYERS
                                                          for a in ("nll", "H", "pmax", "KL_final")]
            stat = {kk: torch.empty(n, device=DEV) for kk in keys}
            for a0 in range(0, n, 256):                          # row chunks bound the memory
                b0 = min(n, a0 + 256); yy = y[a0:b0, None]
                lpF = F.log_softmax(logits[a0:b0].float(), -1)
                stat["nll_final"][a0:b0] = -lpF.gather(1, yy)[:, 0]
                stat["H_final"][a0:b0] = -(lpF.exp() * lpF).sum(-1)
                lps = {}
                for l in LAYERS:
                    h = o.hidden_states[l][0, a0:b0]
                    lp = F.log_softmax(U(ln(h + lenses[l](h))), -1)
                    lps[l] = lp
                    stat[f"nll_{l}"][a0:b0] = -lp.gather(1, yy)[:, 0]
                    stat[f"H_{l}"][a0:b0] = -(lp.exp() * lp).sum(-1)
                    stat[f"pmax_{l}"][a0:b0] = lp.max(-1).values.exp()
                    stat[f"KL_final_{l}"][a0:b0] = (lpF.exp() * (lpF - lp)).sum(-1)
                stat["KL_12_8"][a0:b0] = (lps[12].exp() * (lps[12] - lps[8])).sum(-1)
                del lps, lpF
            fmap[r0:r0 + n] = (o.hidden_states[EXIT][0, :-1] @ P).float().cpu().numpy()
            label = np.array(["natural"] * n, dtype=object)
            for (a, b, lab) in spans:
                for t in range(n):
                    s0, s1 = offs[t + 1]
                    if s0 < b and s1 > a:
                        label[t] = lab
            st = {kk: v.float().cpu().numpy() for kk, v in stat.items()}
            for t in range(n):
                rows.append(dict(doc=k, doc_id=did, domain=dom, pos=t + 1, label=label[t],
                                 **{kk: float(v[t]) for kk, v in st.items()}))
            r0 += n
            if k % 10 == 0:
                print(f"[eval {k+1}/{len(J)}] {time.time()-t0:.0f}s  nll_final={st['nll_final'].mean():.3f} "
                      f"nll_12={st['nll_12'].mean():.3f} nll_8={st['nll_8'].mean():.3f} nll_16={st['nll_16'].mean():.3f}",
                      flush=True)
    fmap.flush()
    pd.DataFrame(rows).to_parquet(RES / "per_token_depth.parquet")
    np.save(RES / "feats_depth_rows.npy", np.array([r0]))


def stage_analyze():
    import analyze as A
    df = pd.read_parquet(RES / "per_token_depth.parquet")
    Fm = np.load(RES / "feats_depth.npy", mmap_mode="r")
    keep = (df.pos >= 64).values
    df = df[keep].reset_index(drop=True)
    X = np.hstack([np.asarray(Fm[np.flatnonzero(keep)], dtype=np.float32),
                   df[["H_12", "pmax_12", "KL_12_8", "H_8"]].values.astype(np.float32)])
    df["base"] = df.doc_id.str.replace("+ids", "", regex=False)
    df["H_L"] = df.H_final            # "big model" entropy in the shared selection table
    out = []
    # exit 8 is not analysed with a learned head: its hidden state was not stored, and the
    # layer-12 features would not yet exist at layer 8 (that would be leakage)
    for ex in (12, 16):
        df["gain_d"] = df[f"nll_{ex}"] - df.nll_final
        df["conf_gap"] = 1 - df[f"pmax_{ex}"]
        # everything up to the exit layer is available: layer-12 features (+ exit-16 scalars for exit 16)
        Xe = X if ex == 12 else np.hstack([X, df[[f"H_{ex}", f"pmax_{ex}"]].values.astype(np.float32)])
        spec = dict(name=f"D_depth_exit{ex}", gain="gain_d", kl=f"KL_final_{ex}", raw=f"nll_{ex}",
                    signals={f"entropy at exit {ex} (early-exit style)": f"H_{ex}",
                             f"1 - max prob at exit {ex} (CALM-style)": "conf_gap",
                             "lens change 8->12 (saturation)": "KL_12_8"},
                    scalars=sorted({f"H_{ex}", f"pmax_{ex}", "KL_12_8", "H_8", "H_12"}))
        R, SEL, COR = A.experiment(df, Xe, spec)
        R.to_csv(RES / f"{spec['name']}_budget_curves.csv", index=False)
        SEL.to_csv(RES / f"{spec['name']}_selection_at_10pct.csv", index=False)
        COR.to_csv(RES / f"{spec['name']}_rank_correlations.csv", index=False)
        XD = A.cross_domain(df, Xe, spec); XD.to_csv(RES / f"{spec['name']}_cross_domain.csv", index=False)
        b50 = R[R.budget == "b50"].groupby(["pool", "policy"]).R.agg(["mean", "std"])
        Rb = R[R.budget != "b50"].copy(); Rb["budget"] = Rb.budget.astype(float)
        piv = (Rb.groupby(["pool", "policy", "budget"]).R.mean().unstack("budget") * 100).round(1)
        piv.columns = [f"R@{int(round(100*c))}%" for c in piv.columns]
        piv["budget for 50% of gap"] = (100 * b50["mean"]).round(1).astype(str) + "% ± " + \
                                       (100 * b50["std"]).round(1).astype(str)
        nat = df[df.domain.isin(["prose", "code"])]
        out.append(f"\n### Exit at layer {ex} of 24: % of the (exit → full depth) loss gap recovered by running "
                   f"the remaining layers on a budget of tokens\n\nMean gap = {nat.gain_d.mean():.3f} nats/token "
                   f"(nll exit {nat[f'nll_{ex}'].mean():.3f} vs full {nat.nll_final.mean():.3f}).\n")
        out.append(piv.to_markdown())
        x = XD.groupby(["test_domain", "policy"])[["R10", "R20", "b50"]].mean()
        out.append("\n\nCross-domain (train on the other domain):\n")
        out.append((100 * x).round(1).to_markdown())
        S = SEL.groupby(["pool", "policy"]).mean(numeric_only=True).drop(columns="seed").round(3)
        out.append("\n\nSelection at 10%:\n")
        out.append(S[S.index.get_level_values(0) == "natural"].to_markdown())
        C_ = COR.groupby(["pool", "signal"]).mean(numeric_only=True).drop(columns="seed").round(3)
        out.append("\n\nRank correlations:\n")
        out.append(C_[C_.index.get_level_values(0) == "natural"].to_markdown())
    (RES / "tables_depth.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    st = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in (("acts", stage_acts), ("lenses", stage_lenses), ("eval", stage_eval),
                     ("analyze", stage_analyze)):
        if st in (name, "all"):
            print(f"=== stage {name} ===", flush=True)
            fn()
