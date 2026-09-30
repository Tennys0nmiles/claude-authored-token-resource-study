"""LaTeX tables for the paper, generated from saved results (no model runs), so that no number in the
paper is copied by hand. Writes paper/tables/*.tex (booktabs rows, \\input by main.tex) and prints the
headline numbers used in the text."""
import json, pathlib, re
import numpy as np
import pandas as pd

ML = pathlib.Path(__file__).resolve().parents[2]
ST, TAB = ML / "analysis" / "stats", ML / "paper" / "tables"; TAB.mkdir(exist_ok=True)
PILOT, GPU = ML / "experiments" / "results", ML / "gpu_results_session1"
BUD = ["0.02", "0.05", "0.1", "0.2", "0.3", "0.5"]


def f1(x):
    return "--" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.1f}"


def split_table(df, pool="natural"):
    """mean and sd over the 5 document splits: {policy: {budget: (mean, sd)}} in % (b50 too)."""
    d = df[df.pool == pool]
    g = d.groupby(["policy", "budget"]).R.agg(["mean", "std"])
    out = {}
    for (pol, b), r in g.iterrows():
        out.setdefault(pol, {})[str(b)] = (100 * r["mean"], 100 * r["std"])
    return out


def write(name, lines):
    (TAB / name).write_text("\n".join(lines) + "\n")


maxsd = []

# ------------------------------------------------------------------ Table 1: signal level (pilot)
A = split_table(pd.read_csv(PILOT / "A_compute_budget_curves.csv", dtype={"budget": str}))
Bm = split_table(pd.read_csv(PILOT / "B_memory_budget_curves.csv", dtype={"budget": str}))
Bf = split_table(pd.read_csv(PILOT / "B_memory_familiarity.csv", dtype={"budget": str}))
Bm.update({k: v for k, v in Bf.items() if k not in Bm})
rowsA = [("random", "random"), ("entropy (BLT-style)", "entropy"),
         ("1 - max prob (CALM-style)", "$1-\\max p$ (CALM-style)"),
         ("layer-6 to layer-12 change", "logit-lens change, layer 6$\\to$12"),
         ("learned: raw surprise", "learned raw-surprise head (control)"),
         ("learned: value (KL), scalars only", "value head, 4 uncertainty scalars"),
         ("learned: value (KL)", "\\textbf{value head}"),
         ("oracle: KL (needs resource)", "oracle (KL; needs the resource)")]
rowsB = [("random", "random"), ("entropy (FLARE-style)", "entropy of the windowed pass"),
         ("learned: raw surprise", "learned raw-surprise head (control)"),
         ("learned: value (KL)", "value head, hidden states only"),
         ("familiarity + entropy only (7 scalars)", "entropy + 6 familiarity features (7 scalars)"),
         ("learned: value (KL) + familiarity", "\\textbf{value head + familiarity}"),
         ("oracle: KL (needs resource)", "oracle (KL; needs the resource)")]
L = []
for title, T, rows in (("(a) Compute: Pythia-160M $\\to$ Pythia-1.4B, both with full context", A, rowsA),
                       ("(b) Memory: Pythia-160M with a 32--63-token window $\\to$ full context", Bm, rowsB)):
    L.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{title}}}}}\\\\")
    for key, lab in rows:
        v = T[key]
        cells = [f1(v[b][0]) for b in ("0.02", "0.1", "0.2", "0.5")] + [f1(v["b50"][0])]
        if key.startswith("learned: value (KL)") and "scalars" not in key and ("familiarity" in key or T is A):
            cells = [f"\\textbf{{{c}}}" for c in cells]
        L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        maxsd += [v[b][1] for b in BUD]
    if T is A:
        L.append("\\midrule")
write("tab_signal.tex", L)
print(f"pilot: max sd across splits = {max(maxsd):.2f} points")
for nm, T, e, v, o in (("compute", A, "entropy (BLT-style)", "learned: value (KL)", "oracle: KL (needs resource)"),
                       ("memory", Bm, "entropy (FLARE-style)", "learned: value (KL) + familiarity",
                        "oracle: KL (needs resource)")):
    print(f"pilot {nm}: entropy/oracle@10 = {T[e]['0.1'][0]/T[o]['0.1'][0]:.2f}, "
          f"value/oracle@10 = {T[v]['0.1'][0]/T[o]['0.1'][0]:.2f}, value/entropy@10 = {T[v]['0.1'][0]/T[e]['0.1'][0]:.2f}, "
          f"b50 {T[e]['b50'][0]:.1f} -> {T[v]['b50'][0]:.1f} ({T[e]['b50'][0]/T[v]['b50'][0]:.2f}x)")

# ------------------------------------------------------------------ Table 2: end-to-end gated attention
BS = pd.read_csv(ST / "e2e_bootstrap.csv"); PR = pd.read_csv(ST / "e2e_paired.csv")
CFG = [("Pythia-160M, 1k, W=64", "Pythia-160M", "1k", 64, GPU / "e2e/e2e_pythia-160m-deduped_W64.csv"),
       ("Pythia-410M, 1k, W=64", "Pythia-410M", "1k", 64, GPU / "e2e/e2e_pythia-410m-deduped_W64.csv"),
       ("Pythia-410M, 1k, W=256", "Pythia-410M", "1k", 256, GPU / "e2e_ablation/e2e_pythia-410m-deduped_W256.csv"),
       ("Pythia-1.4B, 1k, W=64", "Pythia-1.4B", "1k", 64, GPU / "e2e/e2e_pythia-1.4b-deduped_W64.csv"),
       ("Pythia-1.4B, 1k, W=256", "Pythia-1.4B", "1k", 256, GPU / "e2e_ablation/e2e_pythia-1.4b-deduped_W256.csv"),
       ("Qwen2.5-1.5B, 4k, W=256", "Qwen2.5-1.5B", "4k", 256, GPU / "e2e_long/e2e_Qwen2.5-1.5B_W256.csv"),
       ("Qwen2.5-1.5B, 4k, W=1024", "Qwen2.5-1.5B", "4k", 1024, GPU / "e2e_ablation/e2e_Qwen2.5-1.5B_W1024.csv")]
POLS = ["random", "entropy", "fam_rule", "fam_head", "hidden_only", "learned", "oracle"]
RAW = {"random": "random", "entropy": "entropy (local pass)", "fam_rule": "familiarity rule (no training)",
       "fam_head": "familiarity head (7 scalars)", "hidden_only": "learned head (hidden only, ablation)",
       "learned": "learned head (hidden + familiarity)", "oracle": "oracle KL (needs full pass)"}


def pt(cfg, pool, pol, b):
    r = BS[(BS.config == cfg) & (BS.pool == pool) & (BS.policy == pol) & (np.isclose(BS.budget, b))]
    return None if r.empty else r.iloc[0]


def ratio(cfg, pool, comp):
    r = PR[(PR.config == cfg) & (PR.pool == pool) & (PR.comparison == comp)]
    return None if r.empty else r.iloc[0]


def gap_info(path, pool):
    R = pd.read_csv(path)
    R = R[R.domain.isin(["prose", "code"])] if pool == "natural" else R[R.domain == pool]
    u = R[(R.policy == "random") & np.isclose(R.budget, 0.1)]
    return (u.nllA - u.nllF).sum() / u.n.sum(), u.n.sum(), u.nllA.sum() / u.n.sum(), u.nllF.sum() / u.n.sum()


for pool, fname in (("natural", "tab_e2e.tex"), ("prose_ids", "tab_e2e_ids.tex")):
    L = []
    for cfg, model, ctx, W, path in CFG:
        gap, ntok, _, _ = gap_info(path, pool)
        cells = []
        for p in POLS:
            r = pt(cfg, pool, p, 0.1)
            cells.append("--" if r is None else (f"\\textbf{{{r.point:.1f}}}" if p == "learned" else f"{r.point:.1f}"))
        comp = "learned" if pool == "natural" else "fam_rule"
        q = ratio(cfg, pool, comp)
        rat = f"{q.ratio:.2f} {{\\scriptsize[{q.ratio_lo:.2f}, {q.ratio_hi:.2f}]}}"
        L.append(f"{model} & {ctx} & {W} & {gap:.3f} & " + " & ".join(cells) + f" & {rat} \\\\")
        if cfg == "Pythia-1.4B, 1k, W=256":
            L.append("\\midrule")
    write(fname, L)

# familiarity ablation (paired, natural and prose+ids)
L = []
for cfg, model, ctx, W, path in CFG:
    rows = []
    for pool in ("natural", "prose_ids"):
        q = ratio(cfg, pool, "familiarity_contribution")
        h = ratio(cfg, pool, "hidden_only")
        if q is None:
            break
        rows += [f"{pt(cfg, pool, 'hidden_only', 0.1).point:.1f}", f"{pt(cfg, pool, 'learned', 0.1).point:.1f}",
                 f"+{q['diff']:.1f} {{\\scriptsize[{q.diff_lo:.1f}, {q.diff_hi:.1f}]}}",
                 f"{h.ratio:.2f} {{\\scriptsize[{h.ratio_lo:.2f}, {h.ratio_hi:.2f}]}}"]
    if rows:
        L.append(f"{model} & {ctx} & {W} & " + " & ".join(rows) + " \\\\")
write("tab_ablation.tex", L)

# full end-to-end curves (appendix): every policy, every budget, CI at 10%, independent-sum check
L = []
LAB = {"random": "random", "entropy": "entropy", "fam_rule": "familiarity rule", "fam_head": "familiarity head",
       "hidden_only": "value head, hidden only", "learned": "value head + familiarity", "oracle": "oracle (KL)"}
indep_rows = []
for cfg, model, ctx, W, path in CFG:
    R = pd.read_csv(path); R = R[R.domain.isin(["prose", "code"])]
    gap, ntok, nllA, nllF = gap_info(path, "natural")
    L.append(f"\\multicolumn{{7}}{{l}}{{\\emph{{{model}, {ctx} context, $W={W}$: local loss {nllA:.3f}, "
             f"full {nllF:.3f} nats/token, {ntok:,} scored tokens}}}}\\\\")
    for p in POLS:
        if pt(cfg, "natural", p, 0.1) is None:
            continue
        c = [pt(cfg, "natural", p, b) for b in (0.05, 0.1, 0.2, 0.3)]
        g = R[(R.policy == RAW[p]) & np.isclose(R.budget, 0.1)]
        ind = 100 * (g.nllA - g.nll_indep).sum() / (g.nllA - g.nllF).sum()
        indep_rows.append((cfg, p, c[1].point, ind))
        L.append(f"\\quad {LAB[p]} & {c[0].point:.1f} & {c[1].point:.1f} & {{\\scriptsize[{c[1].lo:.1f}, {c[1].hi:.1f}]}} & "
                 f"{c[2].point:.1f} & {c[3].point:.1f} & {ind:.1f} \\\\")
    L.append("\\addlinespace")
blocks, cur = [], []
for line in L:                       # one block per configuration, separated by \addlinespace
    if line == "\\addlinespace":
        blocks.append(cur); cur = []
    else:
        cur.append(line)
blocks.append(cur)
join = lambda bs: sum([b + ["\\addlinespace"] for b in bs], [])[:-1]
write("tab_e2e_full_a.tex", join(blocks[:3]))      # part a: Pythia-160M and -410M; part b: Pythia-1.4B and Qwen
write("tab_e2e_full_b.tex", join(blocks[3:]))
I = pd.DataFrame(indep_rows, columns=["cfg", "pol", "e2e", "indep"])
I = I[I.pol.isin(["entropy", "learned", "oracle"])]
print("e2e minus independent-sum @10% (points):", (I.e2e - I.indep).round(1).describe()[["min", "max", "mean"]].to_dict())

# ------------------------------------------------------------------ Table 3: depth (tuned-lens exits)
DP = [("depth_pythia1.4b", "Pythia-1.4B", 12), ("depth_pythia1.4b", "Pythia-1.4B", 16),
      ("depth_pythia410m", "Pythia-410M", 12), ("depth_pythia410m", "Pythia-410M", 16)]
L = []
for d, model, ex in DP:
    T = split_table(pd.read_csv(GPU / d / f"D_depth_exit{ex}_budget_curves.csv", dtype={"budget": str}))
    md = (GPU / d / "tables_depth.md").read_text()
    m = re.search(rf"Exit at layer {ex} of 24.*?Mean gap = ([\d.]+) nats/token", md, re.S)
    ent, val = f"entropy at exit {ex} (early-exit style)", "learned: value (KL)"
    cols = [ent, f"1 - max prob at exit {ex} (CALM-style)", "lens change 8->12 (saturation)",
            "learned: raw surprise", "learned: value (KL), scalars only", val, "oracle: KL (needs resource)"]
    cells = [f1(T[c]["0.1"][0]) for c in cols]
    cells[5] = f"\\textbf{{{cells[5]}}}"
    rat = T[val]["0.1"][0] / T[ent]["0.1"][0]
    L.append(f"{model} & {ex}/24 & {float(m.group(1)):.2f} & " + " & ".join(cells) +
             f" & {rat:.2f} & {T[ent]['b50'][0]:.1f}$\\to${T[val]['b50'][0]:.1f} \\\\")
    maxsd += [T[c][b][1] for c in cols for b in BUD]
write("tab_depth.tex", L)

# ------------------------------------------------------------------ Table 4: bigger-model ladder
LAD = [("ladderfix_pythia-160m_to_pythia-1.4b", "160M $\\to$ 1.4B"), ("ladderfix_pythia-160m_to_pythia-2.8b", "160M $\\to$ 2.8B"),
       ("ladderfix_pythia-410m_to_pythia-6.9b", "410M $\\to$ 6.9B"), ("ladder_pythia-1.4b_to_pythia-6.9b", "1.4B $\\to$ 6.9B")]
L = []
for d, lab in LAD:
    T = split_table(pd.read_csv(GPU / d / "A_compute_budget_curves.csv", dtype={"budget": str}))
    s = json.load(open(GPU / d / "summary.json"))
    cnt = s["domain_label_counts"]; mn = s["mean_nll"]
    npz, nco = cnt["prose/natural"], cnt["code/natural"]
    gap = (npz * (mn["nll_S"]["prose"] - mn["nll_L"]["prose"]) + nco * (mn["nll_S"]["code"] - mn["nll_L"]["code"])) / (npz + nco)
    cols = ["entropy (BLT-style)", "1 - max prob (CALM-style)", "learned: raw surprise",
            "learned: value (KL)", "oracle: KL (needs resource)"]
    cells = [f1(T[c]["0.1"][0]) for c in cols]; cells[3] = f"\\textbf{{{cells[3]}}}"
    e, v = T["entropy (BLT-style)"], T["learned: value (KL)"]
    L.append(f"{lab} & {gap:.2f} & " + " & ".join(cells) +
             f" & {v['0.1'][0]/e['0.1'][0]:.2f} & {e['b50'][0]:.1f}$\\to${v['b50'][0]:.1f} \\\\")
    maxsd += [T[c][b][1] for c in cols for b in BUD]
write("tab_ladder.tex", L)
# same rows laid out in the 12 columns of the depth table (for the combined compute table)
LW = []
for line in L:
    c = [x.strip() for x in line.rstrip(" \\\\").split("&")]
    LW.append(f"{c[0]} & & {c[1]} & {c[2]} & {c[3]} & & {c[4]} & & {c[5]} & {c[6]} & {c[7]} & {c[8]} \\\\")
write("tab_ladder_wide.tex", LW)
print(f"max sd across splits in all split-based tables = {max(maxsd):.2f} points")

# ------------------------------------------------------------------ Table 5: cross-domain transfer
L = []
xa = pd.read_csv(PILOT / "A_compute_cross_domain.csv"); xb = pd.read_csv(PILOT / "B_memory_cross_domain.csv")
fam = (PILOT / "tables_familiarity.md").read_text()


def famx(dom, pol):
    m = re.search(rf"\('{dom}', '{re.escape(pol)}'\)\s*\|\s*([\d.]+)", fam)
    return float(m.group(1))


def xd(df, dom, pol):
    return 100 * df[(df.test_domain == dom) & (df.policy == pol)].R10.mean()


# long context only: the paper no longer reports value heads for compute or depth
for lab, pc, cp in (
        ("Value head, hidden states only", (xd(xb, "code", "entropy"), xd(xb, "code", "learned on prose only")),
         (xd(xb, "prose", "entropy"), xd(xb, "prose", "learned on code only"))),
        ("Value head + familiarity", (famx("code", "entropy"), famx("code", "learned + familiarity (other domain)")),
         (famx("prose", "entropy"), famx("prose", "learned + familiarity (other domain)"))),
        ("Familiarity head (entropy + 6 familiarity features)", (famx("code", "entropy"), famx("code", "familiarity + entropy (7 scalars) (other domain)")),
         (famx("prose", "entropy"), famx("prose", "familiarity + entropy (7 scalars) (other domain)")))):
    L.append(f"{lab} & {pc[0]:.1f} & {pc[1]:.1f} & {cp[0]:.1f} & {cp[1]:.1f} \\\\")
write("tab_transfer.tex", L)

# ------------------------------------------------------------------ selection of injected identifiers (pilot, 10%)
m = re.search(r"Selection at 10% budget.*?\n\n(.*?)\n\n", fam, re.S)
print("pilot memory: identifier selection at 10% ->\n" + m.group(1))
for f in sorted(TAB.glob("*.tex")):
    print(f.name, len(f.read_text().splitlines()), "rows")

# ------------------------------------------------------------------ per-domain end-to-end (appendix)
L = []
for cfg, model, ctx, W, path in CFG:
    cells = []
    for pool in ("prose", "code"):
        e, v = pt(cfg, pool, "entropy", 0.1), pt(cfg, pool, "learned", 0.1)
        qv, qr = ratio(cfg, pool, "learned"), ratio(cfg, pool, "fam_rule")
        cells += [f"{e.point:.1f}", f"{v.point:.1f}",
                  f"{qv.ratio:.2f} {{\\scriptsize[{qv.ratio_lo:.2f}, {qv.ratio_hi:.2f}]}}",
                  f"{qr.ratio:.2f} {{\\scriptsize[{qr.ratio_lo:.2f}, {qr.ratio_hi:.2f}]}}"]
    L.append(f"{model} & {ctx} & {W} & " + " & ".join(cells) + " \\\\")
write("tab_e2e_domain.tex", L)
P_ = PR[PR.comparison == "learned"]
for pool in ("natural", "prose", "code", "prose_ids"):
    q = P_[P_.pool == pool]
    print(f"value/entropy @10%, {pool}: {q.ratio.min():.2f}-{q.ratio.max():.2f}; min CI low {q.ratio_lo.min():.2f}")
