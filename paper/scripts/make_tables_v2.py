"""LaTeX table rows for the v2 results (5 document splits, Qwen2.5 at 8k tokens, which-vs-whether, attention
timing), generated from analysis/stats/v2_*.csv so that no number is typed by hand. Writes paper/tables/v2_*.tex."""
import pathlib
import numpy as np
import pandas as pd

ML = pathlib.Path(__file__).resolve().parents[2]
ST, TAB = ML / "analysis" / "stats", ML / "paper" / "tables"; TAB.mkdir(exist_ok=True)
S = pd.read_csv(ST / "v2_e2e_summary.csv"); P = pd.read_csv(ST / "v2_e2e_paired.csv")
MT = pd.read_csv(ST / "v2_e2e_meta.csv")
SIZE = {"Pythia-160M": 0, "Pythia-410M": 1, "Pythia-1.4B": 2, "Qwen2.5-1.5B": 3, "Qwen2.5-7B": 4}
MT["o"] = MT.model.map(SIZE)
MT = MT.sort_values(["o", "T", "W"])
CFGS = list(MT.config)


def write(name, lines):
    (TAB / name).write_text("\n".join(lines) + "\n")


def pt(cfg, pool, pol, b=0.1):
    r = S[(S.config == cfg) & (S.pool == pool) & (S.policy == pol) & np.isclose(S.budget, b)]
    return None if r.empty else r.iloc[0]


def pr(cfg, pool, comp):
    r = P[(P.config == cfg) & (P.pool == pool) & (P.comparison == comp)]
    return None if r.empty else r.iloc[0]


def cell_ci(r, fmt="{:.2f}", sign=False):
    if r is None:
        return "--"
    f = (lambda x: ("+" if x >= 0 else "") + fmt.format(x)) if sign else fmt.format
    return f"{f(r['value'])} {{\\scriptsize[{fmt.format(r.lo)}, {fmt.format(r.hi)}]}}"


def label(cfg):
    m = MT[MT.config == cfg].iloc[0]
    return f"{m.model} & {m['T'] // 1024}k & {m.W}"


def group_rules(lines, cfgs):
    out, prev = [], None
    for c, l in zip(cfgs, lines):
        fam = c.split("-")[0]
        if prev is not None and fam != prev:
            out.append("\\midrule")
        out.append(l); prev = fam
    return out


# main end-to-end table (natural text, 10% budget)
rows = []
for c in CFGS:
    m = MT[MT.config == c].iloc[0]
    cells = []
    for p in ("random", "entropy", "fam_head", "hidden_only", "learned", "oracle"):   # the hand-set familiarity rule is not reported
        r = pt(c, "natural", p)
        cells.append("--" if r is None else (f"\\textbf{{{r.point:.1f}}}" if p == "learned" else f"{r.point:.1f}"))
    rows.append(f"{label(c)} & {m.gap:.3f} & " + " & ".join(cells) + f" & {cell_ci(pr(c, 'natural', 'value/entropy'))} \\\\")
write("v2_e2e.tex", group_rules(rows, CFGS))

# familiarity: hidden-only head vs entropy, and the gain from adding familiarity features, by pool
rows = []
for c in CFGS:
    rows.append(f"{label(c)} & {cell_ci(pr(c, 'natural', 'hidden/entropy'))} & "
                f"{cell_ci(pr(c, 'natural', 'familiarity contribution'), '{:.1f}', True)} & "
                f"{cell_ci(pr(c, 'papers26', 'familiarity contribution'), '{:.1f}', True)} & "
                f"{cell_ci(pr(c, 'code', 'familiarity contribution'), '{:.1f}', True)} \\\\")
write("v2_fam.tex", group_rules(rows, CFGS))

# by domain: papers that postdate every model vs code
rows = []
for c in CFGS:
    cells = []
    for pool in ("papers26", "code"):
        e, v = pt(c, pool, "entropy"), pt(c, pool, "learned")
        cells += ["--" if e is None else f"{e.point:.1f}", "--" if v is None else f"{v.point:.1f}",
                  cell_ci(pr(c, pool, "value/entropy"))]
    rows.append(f"{label(c)} & " + " & ".join(cells) + " \\\\")
write("v2_domain.tex", group_rules(rows, CFGS))

# papers with injected identifiers
rows = []
for c in CFGS:
    cells = [("--" if pt(c, "ids", p) is None else f"{pt(c, 'ids', p).point:.1f}")
             for p in ("entropy", "fam_rule", "hidden_only", "learned", "oracle")]
    rows.append(f"{label(c)} & " + " & ".join(cells) + f" & {cell_ci(pr(c, 'ids', 'rule/entropy'))} \\\\")
write("v2_ids.tex", group_rules(rows, CFGS))

# full curves (appendix), one block per configuration
PR = pd.read_csv(ST / "v2_propagation.csv")
LAB = {"random": "random", "entropy": "entropy", "fam_head": "familiarity head",
       "hidden_only": "value head, hidden only", "learned": "value head + familiarity", "oracle": "oracle (KL)"}
blocks = []
for c in CFGS:
    m = MT[MT.config == c].iloc[0]
    L = [f"\\multicolumn{{7}}{{l}}{{\\emph{{{m.model}, {m['T'] // 1024}k, $W={m.W}$: loss {m.local_loss:.3f} local, "
         f"{m.full_loss:.3f} full; {m.tokens_natural:,} tokens}}}}\\\\"]
    for p in LAB:
        r = [pt(c, "natural", p, b) for b in (0.05, 0.1, 0.2, 0.3)]
        if r[1] is None:
            continue
        q = PR[(PR.config == c) & (PR.policy == p)]
        ind = f"{q.indep.iloc[0]:.1f}" if len(q) else "--"
        L.append(f"\\quad {LAB[p]} & {r[0].point:.1f} & {r[1].point:.1f} & {{\\scriptsize[{r[1].lo:.1f}, {r[1].hi:.1f}]}} & "
                 f"{r[2].point:.1f} & {r[3].point:.1f} & {ind} \\\\")
    blocks.append(L)
half = (len(blocks) + 1) // 2
join = lambda bs: sum([b + ["\\addlinespace"] for b in bs], [])[:-1]
write("v2_full_a.tex", join(blocks[:half])); write("v2_full_b.tex", join(blocks[half:]))
(TAB / "v2_full_split.txt").write_text(f"{half}\n")          # how many configurations are in part a

# which vs whether (first split), natural text
BK = ST / "v2_blocks.csv"
if BK.exists():
    K = pd.read_csv(BK)
    bcfgs = [c for c in CFGS if c in set(K.config)]
    spec = [("Whole-query gate, entropy (10\\% of queries)", "gate-only", "sdpa", "entropy", 0.1, -1.0),
            ("Whole-query gate, value head (10\\%)", "gate-only", "sdpa", "learned", 0.1, -1.0),
            ("Whole-query gate, oracle (10\\%)", "gate-only", "sdpa", "oracle", 0.1, -1.0),
            ("Quest-style blocks, every query ($\\rho=10\\%$)", "block", "quest", "", -1.0, 0.1),
            ("Exact top blocks, every query ($\\rho=10\\%$; upper bound)", "block", "exact", "", -1.0, 0.1),
            ("Entropy gate 30\\% + Quest-style blocks ($\\rho=1/3$)", "gate+block", "quest", "entropy", 0.3, 0.333),
            ("Value gate 30\\% + Quest-style blocks ($\\rho=1/3$)", "gate+block", "quest", "learned", 0.3, 0.333),
            ("Entropy gate 20\\% + Quest-style blocks ($\\rho=1/2$)", "gate+block", "quest", "entropy", 0.2, 0.5),
            ("Value gate 20\\% + Quest-style blocks ($\\rho=1/2$)", "gate+block", "quest", "learned", 0.2, 0.5),
            ("Quest-style blocks, every query ($\\rho=1\\%$)", "block", "quest", "", -1.0, 0.01),
            ("\\textbf{Recurrence-addressed blocks only} (no scoring)", "recur", "recur", "", -1.0, 0.0),
            ("Recurrence-addressed $\\cup$ Quest-style ($\\rho=2.5\\%$)", "recur+quest", "recur+quest", "", -1.0, 0.025),
            ("Quest-style blocks, every query ($\\rho=5\\%$)", "block", "quest", "", -1.0, 0.05),
            ("Recurrence-addressed $\\cup$ Quest-style ($\\rho=5\\%$)", "recur+quest", "recur+quest", "", -1.0, 0.05)]
    rows = []
    for name, cond, scorer, gp, b, rho in spec:
        cells, fars, touches = [], [], []
        for c in bcfgs:
            g = K[(K.config == c) & (K.cond == cond) & (K.scorer.fillna("") == scorer) & (K.gate_policy.fillna("") == gp) &
                  np.isclose(K.b, b) & np.isclose(K.rho, rho, atol=1e-3)]
            if g.empty:
                cells.append("--"); continue
            r = g.iloc[0]; fars.append(100 * r.far_frac); touches.append(100 * r.touch_frac)
            cells.append(f"{r.R:.1f}")
        far = f"{min(fars):.1f}--{max(fars):.1f}" if fars and max(fars) - min(fars) >= 0.05 else (f"{fars[0]:.1f}" if fars else "--")
        touch = (f"{min(touches):.0f}--{max(touches):.0f}" if touches and max(touches) - min(touches) >= 0.5
                 else (f"{touches[0]:.0f}" if touches else "--"))
        rows.append(f"{name} & {touch} & {far} & " + " & ".join(cells) + " \\\\")
        if name.startswith("Exact") or name.startswith("Whole-query gate, oracle") or name.startswith("Value gate 20"):
            rows.append("\\addlinespace")
    write("v2_blocks.tex", rows)
    short = {c: f"{MT[MT.config == c].iloc[0].model} ({MT[MT.config == c].iloc[0]['T'] // 1024}k, $W$={MT[MT.config == c].iloc[0].W})"
             for c in bcfgs}
    write("v2_blocks_tabular.tex", ["\\begin{tabular}{lrr" + "r" * len(bcfgs) + "}", "\\toprule",
                                    "Condition & Queries touching (\\%) & Far keys read (\\%) & " + " & ".join(short[c] for c in bcfgs) + " \\\\",
                                    "\\midrule"] + rows + ["\\bottomrule", "\\end{tabular}"])
    (TAB / "v2_blocks_cols.txt").write_text("\n".join(bcfgs) + "\n")

# attention microbenchmark
BE = ST / "v2_bench.csv"
if BE.exists():
    X = pd.read_csv(BE)
    rows = []
    for n, g in X.groupby("n"):
        g = g.set_index("frac")
        rows.append(f"{n // 1024}k & {g.full_flash_ms.iloc[0]:.2f} & {g.local_only_ms.iloc[0]:.2f} & " +
                    " & ".join(f"{g.loc[f, 'gated_ms']:.2f} ({g.loc[f, 'speedup']:.1f}$\\times$)" for f in (0.05, 0.1, 0.2)) + " \\\\")
    write("v2_bench.tex", rows)
print("tables:", sorted(p.name for p in TAB.glob("v2_*")))

# cross-resource atlas (Pythia-1.4B: three resources on the same tokens; Qwen2.5 at 8k: memory for two sizes + scale)
AX = ST / "atlas_cross_allocation.csv"
if AX.exists():
    X = pd.read_csv(AX, index_col=0); FS = pd.read_csv(ST / "atlas_familiar_share.csv").set_index("resource")
    own = {"long context": "oracle for long context", "upper 12 layers": "oracle for depth", "6.9B model": "oracle for 6.9B"}
    lab = {"long context": "Long context (32--63-token window $\\to$ 1k)", "upper 12 layers": "Extra depth (exit at layer 12 $\\to$ 24)",
           "6.9B model": "Larger model (1.4B $\\to$ 6.9B)"}
    rows = []
    for r in ("long context", "upper 12 layers", "6.9B model"):
        others = [X.loc[own[o], r] for o in own if o != r]
        ent = max(X.loc["entropy (window)", r], X.loc["entropy (full context)", r])
        rows.append(f"\\quad {lab[r]} & {X.loc[own[r], r]:.1f} & {min(others):.1f}--{max(others):.1f} & {ent:.1f} & "
                    f"{FS.loc[r, 'gain_share']:.1f} \\\\")
    L = ["\\multicolumn{5}{l}{\\emph{Pythia-1.4B, 1k tokens: three resources on the same 108,593 tokens}}\\\\"] + rows
    QX = ST / "atlas_qwen_cross_allocation.csv"
    if QX.exists():                                   # Qwen: a separate matrix table (realized-gain oracles)
        Q = pd.read_csv(QX, index_col=0)
        cols = ["long context (1.5B)", "long context (7B)", "7B instead of 1.5B"]
        rlab = {"oracle: long context (1.5B)": "Best tokens for long context, 1.5B$^*$",
                "oracle: long context (7B)": "Best tokens for long context, 7B$^*$",
                "oracle: 7B instead of 1.5B": "Best tokens for the 7B model$^*$",
                "entropy of the windowed 1.5B pass": "Highest entropy (windowed 1.5B pass)", "random": "Random tokens"}
        write("v2_atlas_qwen.tex", [f"{rlab[r]} & " + " & ".join(f"{Q.loc[r, c]:.1f}" for c in cols) + " \\\\" for r in rlab])
    write("v2_atlas.tex", L)
print("atlas table written" if AX.exists() else "no atlas stats")
