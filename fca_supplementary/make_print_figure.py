# -*- coding: utf-8 -*-
"""
Print-ready concept lattice figure for the BSDO paper
=====================================================

Renders the same lattices as lattice.py, but sized for print: font sizes are
set in points, the figure width is the publisher's double-column width, and
every text label is measured after layout so that overlaps are reported rather
than discovered in proof.

Outputs PDF, EPS and PNG. Fonts are embedded as TrueType (type 42) because
Type 3 fonts are commonly rejected by publishers.

lattice.py deliberately has no dependencies so that reviewers can rerun the
analysis with a bare Python install. This script is the production step and
needs matplotlib; keeping them apart is intentional.

Usage
-----
    python make_print_figure.py
"""
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lattice import K1, K2, K3, structure, ranks, positions, HIGHLIGHT  # noqa: E402

import matplotlib                                                       # noqa: E402
matplotlib.use('Agg')
matplotlib.rcParams.update({
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'svg.fonttype': 'none',
})
import matplotlib.pyplot as plt                                         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 1 / 25.4

# Elsevier double-column width.
FIG_W = 190 * MM

FS_ATTR = 6.6      # attribute labels
FS_OBJ = 6.6       # object labels
FS_TITLE = 8.5     # panel titles
FS_LEGEND = 6.6

C_ROBUST = '#1f2933'
C_DEP = '#8b95a1'
C_EDGE = '#a9b1ba'
C_RING = '#c8452e'
C_ATTR = '#1a4b8c'
C_SWAP = '#166534'
C_VOLTA = '#9a3412'


def wrap(text, limit=13):
    """Break a label at a space once it exceeds `limit` characters.

    Long attribute names are the binding constraint on horizontal spacing:
    a single-line "colour = process state" is wider than the space available
    between adjacent concepts at this figure width.
    """
    if len(text) <= limit or ' ' not in text.strip():
        return text
    words = text.split(' ')
    best, score = None, None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        s = max(len(a), len(b))
        if score is None or s < score:
            best, score = (a, b), s
    return '\n'.join(best)


def draw(ax, K, title, dx, dy, node_r=2.0):
    """Draw one lattice. Coordinates are arbitrary; the axis is scaled later."""
    nodes, cover, robust, obj_at, att_at = structure(K)
    r = ranks(nodes, cover)
    pos = positions(nodes, cover, r)
    height = max(r.values())
    rings = [frozenset(s) for s in HIGHLIGHT[K['id']]]
    P = lambda n: (pos[n][0] * dx, (height - pos[n][1]) * dy)

    texts = []
    for a, b in cover:
        xa, ya = P(a)
        xb, yb = P(b)
        ax.plot([xa, xb], [ya, yb], color=C_EDGE, lw=0.7, zorder=1,
                solid_capstyle='round')

    for n in nodes:
        x, y = P(n)
        if n in rings:
            ax.add_patch(plt.Circle((x, y), node_r * 2.6, fill=False,
                                    ec=C_RING, lw=1.0, zorder=2))
        if n in robust:
            ax.add_patch(plt.Circle((x, y), node_r, fc=C_ROBUST, ec=C_ROBUST,
                                    lw=0.8, zorder=3))
        else:
            ax.add_patch(plt.Circle((x, y), node_r, fc='white', ec=C_DEP,
                                    lw=0.9, ls=(0, (1.6, 1.2)), zorder=3))

        # Standard FCA placement: attributes up and to the right of the node,
        # objects down and to the left. The lateral offset is what keeps an
        # object label clear of the attribute label belonging to the concept
        # immediately below it, which a purely vertical layout cannot do.
        side = node_r * 1.6
        off = node_r * 1.9
        for a in reversed(att_at.get(n, [])):
            lab = wrap(a)
            t = ax.text(x + side, y + off, lab, ha='left', va='bottom',
                        fontsize=FS_ATTR, color=C_ATTR, fontweight='bold',
                        linespacing=1.15, zorder=4)
            t._anchor = (x, side)
            texts.append(t)
            off += (lab.count('\n') + 1) * FS_ATTR * 1.25
        off = node_r * 1.9
        for g in obj_at.get(n, []):
            lab = wrap(K['label'][g], 15)
            t = ax.text(x - side, y - off, lab, ha='right', va='top',
                        fontsize=FS_OBJ, linespacing=1.15, zorder=4,
                        color=C_SWAP if K['eco'][g] == 'SWAP' else C_VOLTA)
            t._anchor = (x, -side)
            texts.append(t)
            off += (lab.count('\n') + 1) * FS_OBJ * 1.25

    ax.set_title(title, fontsize=FS_TITLE, fontweight='bold', loc='left', pad=4)
    ax.set_aspect('auto')
    ax.axis('off')
    ax.margins(0.06, 0.20)
    return texts


def flip(t):
    """Mirror a label to the other side of its node."""
    x, side = t._anchor
    t.set_position((x - side, t.get_position()[1]))
    t.set_ha('right' if t.get_ha() == 'left' else 'left')
    t._anchor = (x, -side)


def resolve(fig, texts, rounds=6):
    """Flip colliding labels to the far side of their node until none remain.

    A purely geometric layout cannot separate every label pair, because two
    concepts may sit close together with long labels on both. Choosing the
    side per label, rather than fixing it by convention, resolves the rest.
    """
    for _ in range(rounds):
        hits = overlaps(fig, texts)
        if not hits:
            return []
        moved = set()
        for ta, tb in hits:
            for cand in (tb, ta):
                if id(cand) not in moved:
                    flip(cand)
                    moved.add(id(cand))
                    break
    return overlaps(fig, texts)


def overlaps(fig, texts, as_text=False):
    """Report pairs of labels whose rendered boxes intersect."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = [(t, t.get_window_extent(renderer)) for t in texts]
    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ta, ba = boxes[i]
            tb, bb = boxes[j]
            if ta.axes is not tb.axes:
                continue
            if ba.overlaps(bb):
                hits.append((ta.get_text(), tb.get_text()) if as_text else (ta, tb))
    return hits


def build(height_factor=1.16):
    """Three panels stacked, each spanning the full column width.

    Side-by-side panels were tried first and rejected: at half width the
    space between adjacent concepts is narrower than the widest attribute
    label, so labels collide however the spacing is tuned.
    """
    fig = plt.figure(figsize=(FIG_W, FIG_W * height_factor))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 0.90, 1.25],
                          hspace=0.26,
                          left=0.01, right=0.99, top=0.97, bottom=0.055)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[2, 0])

    texts = []
    texts += draw(ax1, K1, '(a)  K1 — battery models', dx=40, dy=26)
    texts += draw(ax2, K2, '(b)  K2 — station device types', dx=40, dy=26)
    texts += draw(ax3, K3, '(c)  K3 — service flows', dx=40, dy=24)

    handles = [
        plt.Line2D([], [], marker='o', ls='', ms=4.2, mfc=C_ROBUST, mec=C_ROBUST,
                   label='robust concept — present under both readings'),
        plt.Line2D([], [], marker='o', ls='', ms=4.2, mfc='white', mec=C_DEP,
                   label='assumption-dependent — pessimistic reading only'),
        plt.Line2D([], [], marker='o', ls='', ms=7.0, mfc='none', mec=C_RING,
                   label='concept discussed in the text'),
    ]
    leg = fig.legend(handles=handles, loc='lower center', ncol=3,
                     fontsize=FS_LEGEND, frameon=False,
                     bbox_to_anchor=(0.5, 0.005), handletextpad=0.5,
                     columnspacing=1.6)
    fig.text(0.5, 0.035,
             'SWAP Energy', color=C_SWAP, fontsize=FS_LEGEND,
             fontweight='bold', ha='right')
    fig.text(0.505, 0.035, '·  ', fontsize=FS_LEGEND, ha='center')
    fig.text(0.512, 0.035, 'Volta', color=C_VOLTA, fontsize=FS_LEGEND,
             fontweight='bold', ha='left')
    fig.text(0.556, 0.035, '·  attribute', color=C_ATTR, fontsize=FS_LEGEND,
             fontweight='bold', ha='left')
    return fig, texts, leg


def main():
    fig, texts, _ = build()

    before = len(overlaps(fig, texts))
    hits = resolve(fig, texts)
    print('Labels drawn        : %d' % len(texts))
    print('Collisions before   : %d' % before)
    print('Collisions remaining: %d' % len(hits))
    for ta, tb in hits[:12]:
        print('    %r  <->  %r' % (ta.get_text(), tb.get_text()))

    # A different stem from the published figure: the figure that goes to
    # the journal is the hand-drawn SVG, verified against this same
    # structure by verify_figure.py. This rendering is kept because it is
    # reproducible from the contexts by running one script, which the
    # hand-drawn one is not.
    stem = os.path.join(HERE, 'fig_lattice_reference')
    for ext, kw in (('pdf', {}), ('eps', {}), ('png', {'dpi': 600})):
        fig.savefig('%s.%s' % (stem, ext), format=ext,
                    bbox_inches='tight', pad_inches=0.02, **kw)
    print()
    print('Figure width        : %.0f mm (publisher double-column)' % (FIG_W / MM))
    print('Smallest type       : %.1f pt' % min(FS_ATTR, FS_OBJ, FS_LEGEND))
    print('Fonts               : embedded TrueType (type 42)')
    print('Written             : fig_lattice_reference.pdf, .eps, .png (600 dpi)')
    print('Note                : the figure published with the paper is')
    print('                      fig_lattice_K1_K3.svg/.pdf, drawn by hand and')
    print('                      checked against this same structure by')
    print('                      verify_figure.py. This is the reproducible')
    print('                      rendering, not the published one.')
    if hits:
        print()
        print('WARNING: labels overlap. Adjust dx/dy in build() before submission.')


if __name__ == '__main__':
    main()
