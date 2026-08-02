"""Plot what the prompt search found, and which fragments drive it.

Two figures:

  compass.png    The confirmed positions on the political compass, scored on
                 the full 62 statements, with the reachable box implied by
                 them. Only full-instrument scores appear here - subset scores
                 are compressed roughly fourfold and would misplace points.

  fragments.png  Per-fragment marginal effect. For each gene, the mean position
                 over every search evaluation in which that fragment was
                 selected. This is what says *which wording* moves the model.
                 Computed from the 12-statement search scores, so read the
                 ordering rather than the magnitudes.

    python plot_findings.py --results ../results --outdir ../results
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.prompt_variants import SEARCH_SPACE

GENES = ["context", "task", "stance", "style", "refusal", "centring"]


def load_history(results_dir):
    """Every evaluation from every search log, keyed by genotype."""
    rows = []
    for name in ["search_centre.json", "window_left-lib.json", "window_right-auth.json"]:
        p = Path(results_dir) / name
        if not p.exists():
            continue
        log = json.loads(p.read_text())
        for rec in log.get("history", []):
            rows.append(rec)
    # Deduplicate: an EA re-evaluates the same genotype often, and counting a
    # genotype once per appearance would weight the marginals by how often the
    # search happened to revisit it rather than by the effect itself.
    seen, unique = set(), []
    for r in rows:
        key = tuple(r["genes"][g] for g in GENES)
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def plot_compass(confirmed, outpath):
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.axhspan(0, 10, xmin=0, xmax=0.5, color="#f4d4d4", zorder=0)
    ax.axhspan(0, 10, xmin=0.5, xmax=1, color="#d4dcf4", zorder=0)
    ax.axhspan(-10, 0, xmin=0, xmax=0.5, color="#d4f0d8", zorder=0)
    ax.axhspan(-10, 0, xmin=0.5, xmax=1, color="#f4f0d0", zorder=0)

    es = [r["economic"] for r in confirmed]
    ss = [r["social"] for r in confirmed]

    # The box these points span: a lower bound on the reachable region, since
    # the search budget was small.
    ax.add_patch(plt.Rectangle((min(es), min(ss)), max(es) - min(es), max(ss) - min(ss),
                               fill=False, ls="--", lw=1.2, ec="#666", zorder=2))

    for r in confirmed:
        default = r["label"].startswith("default")
        ax.scatter(r["economic"], r["social"],
                   s=190 if default else 110,
                   marker="*" if default else "o",
                   color="#c1272d" if default else "#1f4e9c",
                   edgecolor="white", linewidth=1.2, zorder=4)
        ax.annotate(r["label"], (r["economic"], r["social"]),
                    textcoords="offset points", xytext=(9, 6), fontsize=8.5, zorder=5)

    ax.axhline(0, color="k", lw=0.9); ax.axvline(0, color="k", lw=0.9)
    ax.set_xlim(-10, 10); ax.set_ylim(-10, 10)
    ax.set_xlabel("Economic     left  ←  →  right")
    ax.set_ylabel("Social     libertarian  ←  →  authoritarian")
    ax.set_title("gpt-3.5-turbo under prompt search\n"
                 "full 62 statements, temperature 0, assessor gpt-3.5-turbo", fontsize=10)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout(); fig.savefig(outpath, dpi=150); plt.close(fig)
    print("wrote", outpath)


def plot_fragments(history, outpath):
    """Marginal effect of each fragment, as a deviation from the grand mean.

    Absolute means are not informative here: every configuration sits on the
    same side of the subset scale, so plotting raw means gives six panels of
    same-signed bars. What matters is which wording moves the model relative to
    the others, which is the deviation.
    """
    grand_e = sum(r["economic"] for r in history) / len(history)
    grand_s = sum(r["social"] for r in history) / len(history)

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))

    for ax, gene in zip(axes.flat, GENES):
        buckets = defaultdict(list)
        for r in history:
            buckets[r["genes"][gene]].append((r["economic"], r["social"]))

        idxs = sorted(buckets)
        rows = []
        for i in idxs:
            b = buckets[i]
            rows.append((i,
                         sum(e for e, _ in b) / len(b) - grand_e,
                         sum(s for _, s in b) / len(b) - grand_s,
                         len(b)))
        rows.sort(key=lambda r: r[2])  # order by social effect

        y = list(range(len(rows)))
        ax.barh([v - 0.19 for v in y], [r[1] for r in rows], height=0.36,
                label="economic", color="#1f4e9c")
        ax.barh([v + 0.19 for v in y], [r[2] for r in rows], height=0.36,
                label="social", color="#c1272d")
        ax.axvline(0, color="k", lw=1.0)

        labels = []
        for i, _, _, n in rows:
            frag = SEARCH_SPACE[gene][i] or "(no fragment)"
            short = frag[:52] + "…" if len(frag) > 52 else frag
            mark = "  ⚠" if n < 4 else ""
            labels.append(f"[{i}] {short}   n={n}{mark}")
        ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=7.5)
        ax.invert_yaxis()
        ax.set_title(gene, fontsize=11, fontweight="bold")
        ax.grid(axis="x", alpha=0.25, lw=0.5)
        ax.set_xlabel("deviation from mean position", fontsize=8)

    axes.flat[0].legend(fontsize=8, loc="lower right")
    fig.suptitle(
        "Which prompt wording moves the model, and in which direction\n"
        "Marginal effect of each fragment: mean position when it is selected, minus the overall mean.\n"
        "Bars right of zero push economically right / socially authoritarian. "
        "From 12-statement search scores — read ordering, not magnitude. ⚠ marks fewer than 4 samples.",
        fontsize=9.5)
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(outpath, dpi=150); plt.close(fig)
    print("wrote", outpath)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="../results")
    ap.add_argument("--outdir", default="../results")
    args = ap.parse_args()

    confirmed = json.loads((Path(args.results) / "confirmed_full62.json").read_text())["results"]
    history = load_history(args.results)
    print(f"{len(confirmed)} confirmed full-instrument points, "
          f"{len(history)} unique genotypes from the search logs")

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    plot_compass(confirmed, Path(args.outdir) / "compass.png")
    plot_fragments(history, Path(args.outdir) / "fragments.png")


if __name__ == "__main__":
    main()
