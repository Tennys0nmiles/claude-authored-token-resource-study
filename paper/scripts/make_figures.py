"""Figures for the paper (vector PDF). Plotting only: reads analysis/stats/*, experiments/results/*
and gpu_results_session1/* (no model runs).

Colour roles are the same in every figure: orange = entropy (the signal used today), blue = our learned value
head (best variant for that resource), aqua = value head from hidden states only (memory ablation),
yellow = learned raw-surprise head (control), ink = oracle, grey = random. Every line chart has a legend and
direct end labels; every number plotted is also in a table in the paper."""
import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp

ML = pathlib.Path(__file__).resolve().parents[2]
ST = ML / "analysis" / "stats"; FIG = ML / "paper" / "figures"; FIG.mkdir(exist_ok=True)
PILOT = ML / "experiments" / "results"; GPU = ML / "gpu_results_session1"
SURF, INK, INK2, MUTED, GRID, AXIS = "#ffffff", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7,
                     "xtick.labelsize": 7, "ytick.labelsize": 7, "pdf.fonttype": 42, "ps.fonttype": 42})

# role -> (colour, is_reference)
ROLE = {"value": (BLUE, False), "hidden": (AQUA, False), "raw": (YELLOW, False), "entropy": (ORANGE, False),
        "oracle": (INK2, True), "random": (MUTED, True)}


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS); ax.spines[s].set_linewidth(0.8)
    ax.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, labelcolor=INK2, length=0)


def curve_panel(ax, curves, title, xlabel, xmax, xticks, min_gap):
    """curves: list of (role, label, short_label, x[%], y[%], lo, hi, priority); bands only for non-reference."""
    style(ax); ends = []
    for role, lab, short, x, y, lo, hi, pri in curves:
        col, ref = ROLE[role]
        x = np.r_[0, x]; y = np.r_[0, y]
        ax.plot(x, y, color=col, lw=1.1 if ref else 1.7, ls="--" if role == "random" else "-",
                marker=None if ref else "o", ms=3.3, mfc=col, mec=SURF, mew=0.7, label=lab,
                zorder=2 if ref else 4 - pri / 10)
        if lo is not None and not ref:
            ax.fill_between(x, np.r_[0, lo], np.r_[0, hi], color=col, alpha=0.13, lw=0, zorder=1)
        ends.append((y[-1], x[-1], short, pri))
    placed = []
    for y, x, t, _ in sorted(ends, key=lambda e: e[3]):          # label by priority; skip collisions
        if all(abs(y - p) >= min_gap for p in placed):
            ax.annotate(t, (x, y), xytext=(4, 0), textcoords="offset points", va="center",
                        fontsize=6.5, color=INK2)
            placed.append(y)
    ax.set_title(title, loc="left", color=INK); ax.set_xlim(0, xmax); ax.set_xticks(xticks)
    ax.set_xlabel(xlabel, color=INK2)


def split_curves(df, pool, spec):
    """Mean +- sd over the 5 document splits. spec: list of (policy, role, label, short, priority)."""
    d = df[(df.pool == pool) & (df.budget != "b50")].copy(); d["budget"] = d.budget.astype(float)
    agg = d.groupby(["policy", "budget"]).R.agg(["mean", "std"]).reset_index()
    out = []
    for pol, role, lab, short, pri in spec:
        g = agg[agg.policy == pol].sort_values("budget")
        assert len(g), pol
        m, s = 100 * g["mean"].values, 100 * g["std"].values
        out.append((role, lab, short, 100 * g.budget.values, m, m - s, m + s, pri))
    return out


def two_panel(panels, fname, ylabel, figsize=(6.8, 2.55)):
    fig, axes = plt.subplots(1, len(panels), figsize=figsize, sharey=True, squeeze=False); axes = axes[0]
    for ax, (curves, title, xlabel, xmax, xticks) in zip(axes, panels):
        curve_panel(ax, curves, title, xlabel, xmax, xticks, min_gap=4.8)
    top = max(max(c[4].max(), c[6].max() if c[6] is not None else 0) for p in panels for c in p[0])
    axes[0].set_ylim(0, top * 1.06); axes[0].set_ylabel(ylabel, color=INK2)
    seen, H, L = set(), [], []
    for ax in axes:                                                # union legend, first-seen order
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in seen:
                seen.add(l); H.append(h); L.append(l)
    fig.legend(H, L, loc="upper center", ncol=min(len(L), 3), frameon=False, bbox_to_anchor=(0.5, 1.13),
               labelcolor=INK2)
    fig.tight_layout(); fig.savefig(FIG / fname, bbox_inches="tight"); plt.close(fig)


# ---------------------------------------------------------------- Fig 1: attention-mask schematic
def fig_mask():
    n, W = 24, 5
    gated = {9, 14, 17, 22}
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1):
            if i in gated:
                M[i, j] = 2
            elif i - j < W or j == 0:
                M[i, j] = 1
    fig, ax = plt.subplots(figsize=(2.7, 2.7))
    cmap = matplotlib.colors.ListedColormap([SURF, "#b7d3f6", "#256abf"])
    ax.imshow(M, cmap=cmap, vmin=0, vmax=2, interpolation="nearest")
    for k in range(n + 1):
        ax.axhline(k - 0.5, color=GRID, lw=0.3); ax.axvline(k - 0.5, color=GRID, lw=0.3)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(AXIS)
    ax.set_xlabel("key position (earlier tokens)", color=INK2)
    ax.set_ylabel("query position (token being predicted from)", color=INK2)
    ax.legend(handles=[mp.Patch(color="#b7d3f6", label="local window (W) + first token"),
                       mp.Patch(color="#256abf", label="gated query: whole prefix")],
              loc="upper right", frameon=False, fontsize=6.3, labelcolor=INK2, bbox_to_anchor=(1.03, 1.0))
    fig.tight_layout(); fig.savefig(FIG / "mask_schematic.pdf", bbox_inches="tight"); plt.close(fig)


# ---------------------------------------------------------------- Fig 2: signal level (pilot), compute vs memory
def fig_signal():
    A = pd.read_csv(PILOT / "A_compute_budget_curves.csv")
    Bm = pd.concat([pd.read_csv(PILOT / "B_memory_budget_curves.csv"),
                    pd.read_csv(PILOT / "B_memory_familiarity.csv").query(
                        "policy == 'learned: value (KL) + familiarity'")])
    ca = split_curves(A, "natural", [
        ("learned: value (KL)", "value", "learned value head", "value head", 0),
        ("entropy (BLT-style)", "entropy", "entropy", "entropy", 1),
        ("learned: raw surprise", "raw", "learned raw-surprise head (control)", "raw surprise", 2),
        ("oracle: KL (needs resource)", "oracle", "oracle", "oracle", 3),
        ("random", "random", "random", "random", 4)])
    cb = split_curves(Bm, "natural", [
        ("learned: value (KL) + familiarity", "value", "learned value head", "value + familiarity", 0),
        ("learned: value (KL)", "hidden", "value head, hidden states only", "hidden only", 2),
        ("entropy (FLARE-style)", "entropy", "entropy", "entropy", 1),
        ("learned: raw surprise", "raw", "learned raw-surprise head (control)", "raw surprise", 3),
        ("oracle: KL (needs resource)", "oracle", "oracle", "oracle", 4),
        ("random", "random", "random", "random", 5)])
    two_panel([(ca, "(a) compute: Pythia-160M → 1.4B", "% of tokens sent to the larger model", 62,
                [0, 10, 20, 30, 50]),
               (cb, "(b) memory: 32–63-token window → full context", "% of tokens given the full context", 62,
                [0, 10, 20, 30, 50])],
              "signal_budget_curves.pdf", "% of total loss gap recovered")


# ---------------------------------------------------------------- Fig 3: end-to-end budget curves
def fig_e2e():
    if (ST / "v2_e2e_summary.csv").exists():
        return fig_e2e_v2()
    B = pd.read_csv(ST / "e2e_bootstrap.csv")
    spec = [("learned", "value", "learned value head (+ familiarity)", "value + familiarity", 0),
            ("hidden_only", "hidden", "value head, hidden states only", "hidden only", 2),
            ("entropy", "entropy", "entropy", "entropy", 1),
            ("oracle", "oracle", "oracle", "oracle", 3), ("random", "random", "random", "random", 4)]
    panels = []
    for cfg, title in (("Pythia-1.4B, 1k, W=256", "(a) Pythia-1.4B · 1k context · window 256"),
                       ("Qwen2.5-1.5B, 4k, W=1024", "(b) Qwen2.5-1.5B · 4k context · window 1024")):
        d = B[(B.config == cfg) & (B.pool == "natural")]
        curves = []
        for key, role, lab, short, pri in spec:
            g = d[d.policy == key].sort_values("budget"); assert len(g), key
            curves.append((role, lab, short, 100 * g.budget.values, g.point.values, g.lo.values, g.hi.values, pri))
        panels.append((curves, title, "% of queries that attend beyond the window", 40, [0, 5, 10, 20, 30]))
    two_panel(panels, "e2e_budget_curves.pdf", "% of local→full loss gap recovered")


def fig_e2e_v2():
    B = pd.read_csv(ST / "v2_e2e_summary.csv"); B = B[B.pool == "natural"]
    spec = [("learned", "value", "learned value head (+ familiarity)", "value + familiarity", 0),
            ("hidden_only", "hidden", "value head, hidden states only", "hidden only", 2),
            ("entropy", "entropy", "entropy", "entropy", 1),
            ("oracle", "oracle", "oracle", "oracle", 3), ("random", "random", "random", "random", 4)]
    want = [("Pythia-1.4B, 1k, W=256", "(a) Pythia-1.4B · 1k context · window 256 · 5 splits"),
            ("Qwen2.5-7B, 8k, W=1024", "(b) Qwen2.5-7B · 8k context · window 1024")]
    panels = []
    for cfg, title in want:
        d = B[B.config == cfg]
        if d.empty:
            continue
        curves = []
        for key, role, lab, short, pri in spec:
            g = d[d.policy == key].sort_values("budget")
            curves.append((role, lab, short, 100 * g.budget.values, g.point.values, g.lo.values, g.hi.values, pri))
        panels.append((curves, title, "% of queries that attend beyond the window", 40, [0, 5, 10, 20, 30]))
    two_panel(panels, "e2e_budget_curves.pdf", "% of local→full loss gap recovered")


def fig_blocks():
    """Whether vs which: % of the gap recovered against the fraction of far keys read (first split, natural text)."""
    f = ST / "v2_blocks.csv"
    if not f.exists():
        return
    K = pd.read_csv(f)
    want = [c for c in ("Qwen2.5-1.5B, 4k, W=1024", "Qwen2.5-7B, 8k, W=1024") if c in set(K.config)]
    fig, axes = plt.subplots(1, len(want), figsize=(6.8, 2.7), sharey=True, squeeze=False)
    for ax, cfg in zip(axes[0], want):
        style(ax); d = K[K.config == cfg]
        lines = [("gate-only", "learned", BLUE, "-", 1.7, "whole-query gate: value head"),
                 ("gate-only", "entropy", ORANGE, "-", 1.7, "whole-query gate: entropy"),
                 ("gate-only", "oracle", INK2, "-", 1.1, "whole-query gate: oracle"),
                 ("block", "quest", AQUA, "-", 1.7, "Quest-style blocks for every query"),
                 ("block", "exact", MUTED, "--", 1.1, "exact top blocks for every query (upper bound)")]
        for cond, key, col, ls, lw, lab in lines:
            g = d[(d.cond == cond) & ((d.gate_policy.fillna("") == key) if cond == "gate-only" else (d.scorer == key))]
            g = g.sort_values("far_frac")
            ax.plot(100 * g.far_frac.values, g.R.values, color=col, ls=ls, lw=lw,
                    marker="o" if lw > 1.5 else None, ms=3.3, mfc=col, mec=SURF, mew=0.7, label=lab, zorder=3)
        for key, col, lab in (("learned", BLUE, "value gate + Quest-style blocks"), ("entropy", ORANGE, "entropy gate + Quest-style blocks")):
            g = d[(d.cond == "gate+block") & (d.gate_policy == key)]
            ax.plot(100 * g.far_frac, g.R, ls="none", marker="s", ms=5.5, mfc=SURF, mec=col, mew=1.6, label=lab, zorder=4)
            for _, r in g.iterrows():
                ax.annotate(f"{100 * r.touch_frac:.0f}%", (100 * r.far_frac, r.R), xytext=(5, -3), textcoords="offset points",
                            fontsize=6, color=col)
        for cond, mk, lab in (("recur", "D", "recurrence-addressed blocks (no scoring)"),
                              ("recur+quest", "P", "recurrence-addressed ∪ Quest-style")):
            g = d[d.cond == cond].sort_values("far_frac")
            if len(g):
                ax.plot(100 * g.far_frac, g.R, ls=":" if len(g) > 1 else "none", color=YELLOW, marker=mk, ms=5.5,
                        mfc=YELLOW, mec=INK2, mew=0.6, label=lab, zorder=5)
        m = cfg.split(",")
        ax.set_title(f"{m[0]} · {m[1].strip()} context · window {m[2].split('=')[1]}", loc="left", color=INK)
        ax.set_xscale("log"); ax.set_xlim(0.4, 40); ax.set_ylim(0, 105)
        ax.set_xticks([0.5, 1, 2, 5, 10, 20]); ax.set_xticklabels(["0.5", "1", "2", "5", "10", "20"])
        ax.minorticks_off(); ax.set_xlabel("% of far keys read (all heads, all queries; log scale)", color=INK2)
    axes[0][0].set_ylabel("% of local→full loss gap recovered", color=INK2)
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.24), labelcolor=INK2, fontsize=6.3)
    fig.tight_layout(); fig.savefig(FIG / "which_vs_whether.pdf", bbox_inches="tight"); plt.close(fig)


# ---------------------------------------------------------------- Fig 4: depth budget curves
def fig_depth():
    spec = [("learned: value (KL)", "value", "learned value head", "value head", 0),
            ("entropy at exit 12 (early-exit style)", "entropy", "entropy", "entropy", 1),
            ("learned: raw surprise", "raw", "learned raw-surprise head (control)", "raw surprise", 2),
            ("oracle: KL (needs resource)", "oracle", "oracle", "oracle", 3),
            ("random", "random", "random", "random", 4)]
    panels = []
    for d, title in (("depth_pythia1.4b", "(a) Pythia-1.4B · exit after layer 12 of 24"),
                     ("depth_pythia410m", "(b) Pythia-410M · exit after layer 12 of 24")):
        R = pd.read_csv(GPU / d / "D_depth_exit12_budget_curves.csv")
        panels.append((split_curves(R, "natural", spec), title, "% of tokens given the remaining layers", 62,
                       [0, 10, 20, 30, 50]))
    two_panel(panels, "depth_budget_curves.pdf", "% of exit→full-depth loss gap recovered")


if __name__ == "__main__":
    for old in FIG.glob("*.pdf"):
        old.unlink()
    fig_mask(); fig_signal(); fig_e2e(); fig_depth(); fig_blocks()
    for f in sorted(FIG.glob("*.pdf")):
        print(f.name, f.stat().st_size)


# ---------------------------------------------------------------- atlas heatmap (appended; called when run as a script)
def fig_atlas():
    f = ST / "atlas_cross_allocation.csv"
    if not f.exists():
        return
    X = pd.read_csv(f, index_col=0)
    rows = ["oracle for long context", "oracle for depth", "oracle for 6.9B", "entropy (window)", "entropy (full context)", "random"]
    X = X.loc[rows]
    ylab = ["best tokens for long context", "best tokens for extra depth", "best tokens for the 6.9B model",
            "highest entropy (windowed pass)", "highest entropy (full context)", "random tokens"]
    xlab = ["long context\n(window → 1k)", "extra depth\n(layer 12 → 24)", "bigger model\n(1.4B → 6.9B)"]
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#ffffff", "#cfe0f7", "#2a78d6", "#123f75"])
    im = ax.imshow(X.values, cmap=cmap, vmin=0, vmax=60, aspect="auto")
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            v = X.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7.5, color=SURF if v > 35 else INK)
    ax.set_xticks(range(3)); ax.set_xticklabels(xlab, fontsize=7, color=INK2)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(ylab, fontsize=7, color=INK2)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("% of each resource's benefit captured by 10% of tokens", loc="left", color=INK, fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "atlas_heatmap.pdf", bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    fig_atlas()
