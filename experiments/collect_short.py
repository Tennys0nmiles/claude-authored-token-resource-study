"""Second pass (cheap model only): hidden-state features of S when it sees only its short
local window (32-63 tokens). These are the features a cheap local model would have when
deciding whether to fetch long-range context (the "retrieval / memory read" decision).

Rebuilds exactly the same job list and target->window assignment as collect.py.
"""
import json, random, pathlib, time
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

import importlib.util, sys, types
ROOT = pathlib.Path(__file__).parent

# Reuse clean() / inject_ids() / constants from collect.py without loading its models:
# execute only the source above the model-loading lines.
src = (ROOT / "collect.py").read_text()
head = src[: src.index("tok = AutoTokenizer")]
funcs = src[src.index("def clean(text):"): src.index("def _stats(")]
C = types.ModuleType("collect_head"); C.__file__ = str(ROOT / "collect.py")
exec(head + funcs, C.__dict__)

tok = AutoTokenizer.from_pretrained(C.S_NAME)
C.BOS = tok.eos_token_id
S = AutoModelForCausalLM.from_pretrained(C.S_NAME, dtype=torch.float32).eval().to(C.DEV)
C.FEAT_LAYERS = (S.config.num_hidden_layers // 2, S.config.num_hidden_layers)
torch.set_num_threads(10)


@torch.inference_mode()
def short_feats(ids):
    n = ids.shape[0]
    WIN, STRIDE = C.WIN, C.STRIDE
    starts = list(range(0, max(1, n - WIN) + 1, STRIDE))
    if starts[-1] + WIN < n:
        starts.append(n - WIN)
    D = S.config.hidden_size * len(C.FEAT_LAYERS)
    out = np.full((n - 1, D), np.nan, dtype=np.float32)
    done = np.zeros(n - 1, dtype=bool)
    for w0 in range(0, len(starts), 16):
        grp = starts[w0:w0 + 16]
        hs = S(torch.stack([ids[s:s + WIN] for s in grp]).to(C.DEV), output_hidden_states=True).hidden_states
        h = torch.cat([hs[l] for l in C.FEAT_LAYERS], -1)[:, :-1].float().cpu()      # [g, WIN-1, D]
        for g, s in enumerate(grp):
            lo = 0 if s == 0 else STRIDE - 1
            for j in range(lo, WIN - 1):
                t = s + j
                if t < n - 1 and not done[t]:
                    out[t] = h[g, j].numpy(); done[t] = True
    assert done.all()
    return out.astype(np.float16)


def main():
    docs = [json.loads(l) for l in open(C.DOCS)]
    rng = random.Random(1)
    jobs = [(d["id"], d["domain"], C.clean(d["text"]), []) for d in docs]
    for d in docs:
        if d["domain"] == "prose":
            txt, spans = C.inject_ids(C.clean(d["text"]), rng)
            if txt:
                jobs.append((d["id"] + "+ids", "prose_ids", txt, spans))
    ref = pd.read_parquet(C.RES / "per_token.parquet", columns=["doc_id", "pos"])
    n_expected = len(ref)
    D = S.config.hidden_size * len(C.FEAT_LAYERS)
    fmap = np.lib.format.open_memmap(C.RES / "feats_Ss.npy", mode="w+",
                                     dtype=np.float16, shape=(n_expected, D))
    row0, t0, ids_seen = 0, time.time(), []
    for i, (did, dom, text, spans) in enumerate(jobs):
        enc = tok(text, add_special_tokens=False)
        ids = [C.BOS] + enc["input_ids"][: C.T]
        if len(ids) < 256:
            continue
        f = short_feats(torch.tensor(ids))
        fmap[row0:row0 + len(f)] = f; row0 += len(f); ids_seen += [did] * len(f)
        if i % 20 == 0:
            print(i, did, row0, f"{(time.time()-t0)/60:.1f} min", flush=True)
    fmap.flush()
    assert row0 == n_expected and list(ref.doc_id) == ids_seen, "row alignment mismatch"
    print("done; rows aligned:", row0)


if __name__ == "__main__":
    main()
