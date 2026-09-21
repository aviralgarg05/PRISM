"""Lead figure: the size of each measurement component, in the instrument's own units.

Each bar is the size (absolute value) of one measured shift of one persona's social
coordinate when a single component of the audit changes and everything else stays at the
configuration the source used. It is one shift, chosen under the definition in the
provenance table of components_caption.md; it is not necessarily the largest for its
component, and the caption's provenance lists the larger ones FINDINGS records. The social
axis runs from -10 to +10. Every input number is quoted from FINDINGS.md, section given;
where a bar is a difference of two quoted numbers, the pair is listed in SOURCE_PAIRS and
the script checks the arithmetic before drawing.

The bars are drawn in the order of where each component originates in one audit, not
sorted by size. FINDINGS.md, "How one audit works", has four stages (persona, essay
writer, assessor, tally against the key); the elicitation-route stage is added to that
flow here, not taken from it, and the safety bar sits under the writer, whose declines it
concerns, although the refusal rule it varies is applied at scoring. The bars are single
chosen instances on different models and protocols, one from another audit, so no pair's
order is established: the figure ranks nothing and does not apportion variance.

Run from the repository root:

    .venv/bin/python results/figures/components.py

Writes components.png (300 dpi) and components.pdf next to this file.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import transforms  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402


# ---------------------------------------------------------------------------
# The data. One row per component, in order of origin in the audit (drawn top to bottom):
#   value       headline magnitude, instrument units: the size (absolute value) of the
#               shift on the social axis; the caption gives both ends, so the direction
#               is recoverable from the caption
#   component   bar label, first line
#   short       bar label, second line
#   anchor      FINDINGS.md section the value comes from (pre-registrations are designs,
#               cited in the caption's provenance table, never as the value's anchor)
#   definition  what exactly is held fixed and what moves
# ---------------------------------------------------------------------------
COMPONENTS = [
    (4.33, "Prompt", "one answer-format sentence", "§40",
     "mistral H* pccentrist, gpt-4o-mini assessing, ungated, refusals as Agree; only "
     "the sentence telling it to answer Agree or Disagree is removed: +1.863 against "
     "-2.468. Design: seventh pre-registration. 12 replicates per arm, but only 3.7 "
     "and 3.6 distinct essays per statement (§40)"),
    (6.92, "Model", "one persona, two models", "§32",
     "pcxrightauth, same persona text, gpt-4o-mini assessing, full instrument: "
     "+7.39 on gpt-3.5-turbo (its H*, confirmed at n=12, §32; the matched-parent "
     "re-run's second n=12 confirmation gives +7.320, §39) against +0.47 on mistral "
     "(from mistral's H* candidate confirmation, 1.0 to 3.7 distinct essays per "
     "statement, §36; results/m3/hstar_m3c_0.json and hstar_m3c_1.json)"),
    (6.64, "Safety policy", "safety decline read as a stance", "§34",
     "gemma3 facist, declined on 62 of 62 statements, one enumeration run (§33); the "
     "essays, the model and its safety behaviour are held fixed and only the audit's "
     "reading of the declines changes: ungated, as PRISM scores them as published "
     "(-6.64: the 62 - 10 = 52 essays written after the decline that the assessor did "
     "not label Refused scored as stances, its 10 Refused scored as 'Agree'), against "
     "gated as refusals carrying no position (0.00, the Neutral rule's value for a "
     "fully refused persona and the instrument origin, §38). Gated and with each "
     "refusal scored as 'Agree', as the published Agree coding does, the persona "
     "sits at +2.41, a swing of "
     "2.41 - (-6.64) = 9.05, so the bar's length depends on the refusal rule"),
    (4.15, "Elicitation route", "essay or forced choice", "§39",
     "gpt-3.5-turbo search winner, same persona text and key: essays labelled by the "
     "assessor (+7.384) against choosing one of the four options itself (+3.235). "
     "Design: eighth pre-registration. The forced-choice replicates repeat: at "
     "temperature 0, gpt-3.5-turbo and gpt-4o-mini gave between 1 and 5 distinct "
     "answer sets across the six replicates of one option order (§39). The route "
     "does not move personas one way: the hand-written authoritarian personas "
     "score higher when asked directly, by +1.17 to +2.22 on all three models (§39)"),
    (1.77, "Assessor", "two strong assessors", "§41",
     "mistral search winner, the same 12 cached replicates (4.7 distinct essays per "
     "statement) "
     "labelled by gpt-4o instead of gpt-4o-mini; position moves down by 1.774 "
     "(§41), from +5.243 (§32) to 5.243 - 1.774 = +3.469, the difference D between "
     "personas at most 0.65. On mistral's boundary essays the "
     "two agree on direction for 99.3% of statements and 811 disagreements are "
     "'Strongly agree' against 'Agree', which the zero weight on 'Agree' turns into "
     "position. Design: sixth pre-registration"),
    (2.68, "Scoring instrument", "coding of “Agree”, Motoki data", "§37",
     "Motoki et al.'s radical-republican condition, their deposited answers, weights "
     "and transform; only 'agree' moves from zero weight to the midpoint: social "
     "+4.41 against +1.73. One published audit; their conclusion compares "
     "conditions, and the re-score does not overturn it (§37)"),
]

# Where a bar is |a - b| of two quoted numbers: (a, b), both in the anchor section.
# The assessor bar is quoted directly as a shift ("search winner moves -1.774", §41).
SOURCE_PAIRS = {
    "Prompt": (1.863, -2.468),            # §40, delta +4.331
    "Model": (7.39, 0.47),                # §32
    "Safety policy": (-6.64, 0.00),       # §34, ungated against gated, Neutral rule
    "Elicitation route": (7.384, 3.235),  # §39, Delta -4.150 (from unrounded means)
    "Scoring instrument": (4.41, 1.73),   # §37, shift -2.68
}

# §41: the equivalence bound for differences, widened to the upper 95% limit of the
# measured assessor term; §41 applies it to D, the forced-choice Delta and the
# `pcleftlib` ablation delta (§40). The prompt bar is an ablation delta of the same
# kind, on mistral, which §41 does not re-read; the route bar is a forced-choice Delta.
# It is not a test between bars.
RESOLUTION_BOUND = 0.89

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BAR = "#6b7680"        # one neutral slate for every bar
INK = "#0b0b0b"        # primary text
INK_2 = "#52514e"      # secondary text
RULE = "#8a8984"       # axis rule and ticks
REF = "#a9a79f"        # reference line

FIG_W, FIG_H = 3.3, 2.5            # inches, single column
LEFT, RIGHT = 1.58, 0.10           # inches of margin
BOTTOM, TOP = 0.39, 0.04
X_MAX = 8.0
BAR_FRAC = 0.56                    # bar thickness as a share of its band
CORNER_PT = 2.0                    # rounded data end, square at the baseline

OUT_DIR = Path(__file__).resolve().parent


# Derived numbers the caption and its provenance quote that are not bars:
# (label, a, b, stated a - b).
CAPTION_DERIVED = [
    ("safety, Agree-rule swing (§34)", 2.41, -6.64, 9.05),
    ("weak assessor, social axis (§8)", 1.64, -4.56, 6.20),
    ("one social clause, gpt-4o-mini ctrlleftauth against pcleftauth (§24; older "
     "configuration, under §29's caveat)", 4.46, -2.46, 6.92),
    ("prompt, paper prompt to fragment-search maximum, gpt-3.5-turbo (§21, §23)",
     6.15, -4.18, 10.33),
    ("prompt, paper prompt to pcxrightauth, gpt-3.5-turbo (§21, §28)", 7.30, -4.18, 11.48),
    ("assessor bar, gpt-4o end (§32, §41)", 5.243, 1.774, 3.469),
    ("facist, essays after the decline not labelled Refused (§34)", 62, 10, 52),
    ("essay-route D, gpt-3.5-turbo re-run (§39)", 7.384, 7.320, 0.064),
    # §32 quotes mistral's +0.47 only to two decimals; the run files' unrounded means
    # give a difference that rounds one hundredth higher (disclosed in the caption).
    ("model bar with §32's table value for H* (§32)", 7.393, 0.47, 6.923),
    ("model bar with the re-run H* (§39, §32)", 7.320, 0.47, 6.85),
    ("that bar minus safety policy", 6.85, 6.64, 0.21),
    # §41: gpt-3.5-turbo's search winner moves +1.021 under gpt-4o, on the cells whose
    # gpt-4o-mini D (+0.064) is §39's essay-route D, so on §39's essay arm.
    ("route Delta with the essay arm read by gpt-4o (§39, §41)",
     3.235, 7.384 + 1.021, -5.170),
    ("gap, model and safety policy (an example, not a test)", 6.92, 6.64, 0.28),
    ("gap, prompt and elicitation route (an example, not a test)", 4.33, 4.15, 0.18),
]


def check_arithmetic():
    """Every derived bar must equal the difference of its two quoted numbers."""
    for value, component, *_ in COMPONENTS:
        if component not in SOURCE_PAIRS:
            continue
        a, b = SOURCE_PAIRS[component]
        derived = abs(a - b)
        # 0.006 allows for a quoted delta computed from unrounded means (4.149 vs 4.150).
        assert abs(derived - value) < 0.006, (component, a, b, derived, value)
        print(f"{component:<20} |{a:+.3f} - {b:+.3f}| = {derived:.3f}  shown {value:.2f}")
    for label, a, b, stated in CAPTION_DERIVED:
        assert abs((a - b) - stated) < 0.005, (label, a, b, stated)
        print(f"caption: {label}: {a:+g} - ({b:+g}) = {a - b:.3f}")


def rounded_bar(x_len, y_mid, height, rx, ry):
    """A horizontal bar from x=0, square at the baseline, rounded at the data end.

    rx and ry are the corner radius in data units on each axis, so the corner is
    circular on the page whatever the axes' aspect.
    """
    k = 0.5523  # cubic Bezier approximation of a quarter circle
    y0, y1 = y_mid - height / 2, y_mid + height / 2
    xe = x_len
    verts = [
        (0, y0),
        (xe - rx, y0),
        (xe - rx + k * rx, y0), (xe, y0 + ry - k * ry), (xe, y0 + ry),
        (xe, y1 - ry),
        (xe, y1 - ry + k * ry), (xe - rx + k * rx, y1), (xe - rx, y1),
        (0, y1),
        (0, y0),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.LINETO,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CLOSEPOLY,
    ]
    return MplPath(verts, codes)


def draw():
    rows = COMPONENTS  # order of origin, top to bottom; deliberately not sorted by size
    n = len(rows)

    plt.rcParams.update({
        "font.family": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.unicode_minus": True,
    })

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax_w = FIG_W - LEFT - RIGHT
    ax_h = FIG_H - BOTTOM - TOP
    ax = fig.add_axes([LEFT / FIG_W, BOTTOM / FIG_H, ax_w / FIG_W, ax_h / FIG_H])

    # First stage of the audit at the top; headroom above for the bound's two-line label.
    y_lo, y_hi = -0.55, n - 0.5 + 0.86
    ax.set_xlim(0, X_MAX)
    ax.set_ylim(y_lo, y_hi)

    # Corner radius in data units, from the fixed axes geometry.
    pt_per_x = ax_w * 72 / X_MAX
    pt_per_y = ax_h * 72 / (y_hi - y_lo)
    rx, ry = CORNER_PT / pt_per_x, CORNER_PT / pt_per_y

    # Reference line for the resolution bound, behind the bars.
    label_y = n - 0.5 + 0.42
    ax.plot([RESOLUTION_BOUND, RESOLUTION_BOUND], [y_lo, label_y + 0.30],
            color=REF, lw=0.6, dashes=(2.2, 1.6), zorder=1, solid_capstyle="butt")
    ax.text(RESOLUTION_BOUND, label_y, "resolution bound for differences\n0.89 (§41)",
            transform=transforms.offset_copy(ax.transData, fig, x=3, units="points"),
            ha="left", va="center", fontsize=6.3, color=INK_2, linespacing=1.15)

    label_tf = transforms.blended_transform_factory(ax.transAxes, ax.transData)
    for i, (value, component, short, anchor, _definition) in enumerate(rows):
        y = n - 1 - i
        ax.add_patch(PathPatch(rounded_bar(value, y, BAR_FRAC, rx, ry),
                               facecolor=BAR, edgecolor="none", zorder=2))
        ax.text(value, y, f"{value:.2f}",
                transform=transforms.offset_copy(ax.transData, fig, x=3, units="points"),
                ha="left", va="center", fontsize=7, color=INK)
        ax.text(-0.035, y, component,
                transform=transforms.offset_copy(label_tf, fig, y=3.9, units="points"),
                ha="right", va="center", fontsize=7.3, fontweight="bold", color=INK)
        ax.text(-0.035, y, f"{short}, {anchor}",
                transform=transforms.offset_copy(label_tf, fig, y=-4.1, units="points"),
                ha="right", va="center", fontsize=6.3, color=INK_2)

    # Chrome: a single hairline baseline axis, no gridlines, no y ticks.
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.spines["bottom"].set_linewidth(0.6)
    ax.set_yticks([])
    ax.set_xticks(range(0, int(X_MAX) + 1, 2))
    ax.tick_params(axis="x", colors=RULE, labelcolor=INK_2, labelsize=6.8,
                   width=0.6, length=2.5, pad=2)
    ax.set_xlabel("size of shift in social position, instrument units",
                  fontsize=7.2, color=INK, labelpad=3, loc="right")

    # Layout check: no text may run off the page at this fixed single-column size.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    page = fig.bbox
    texts = list(ax.texts) + [ax.xaxis.label] + list(ax.get_xticklabels())
    for t in texts:
        bb = t.get_window_extent(renderer)
        assert bb.x0 >= page.x0 - 0.5 and bb.x1 <= page.x1 + 0.5, (t.get_text(), bb, page)
        assert bb.y0 >= page.y0 - 0.5 and bb.y1 <= page.y1 + 0.5, (t.get_text(), bb, page)

    png = OUT_DIR / "components.png"
    pdf = OUT_DIR / "components.pdf"
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, facecolor="white", metadata={"CreationDate": None})
    plt.close(fig)
    return png, pdf


if __name__ == "__main__":
    check_arithmetic()
    for path in draw():
        print(f"wrote {path} ({path.stat().st_size:,} bytes)")
