# -*- coding: utf-8 -*-
"""
Formal Concept Analysis for the Battery Swap Domain Ontology (BSDO)
===================================================================

Reproduces the concept lattices reported in the paper and the figure that
accompanies them, from the formal contexts in this directory.

Cell values
-----------
    x   the attribute applies, directly observed
    .   absent  -- the attribute genuinely does not apply
    ?   unarticulated -- not exposed by the source, but possibly present

The distinction between "absent" and "unarticulated" follows Fu (2016).
Recording 0 for something that may exist but was never articulated is an
inference, not an observation, and a lattice built on such cells makes claims
the data does not support.

Two lattices are therefore computed per context:

    pessimistic   ? read as 0   (the attribute does not apply)
    optimistic    ? read as 1   (the attribute applies)

A concept whose extent occurs in *both* lattices is called **robust**. Only
robust concepts were used to derive classes in the ontology. Concepts occurring
in one variant only are **assumption-dependent** and are reported as such.

Usage
-----
    python lattice.py            verify counts, write contexts, write the
                                 screen figure fig_lattice_screen.svg

The figure published with the paper, fig_lattice_K1_K3.svg, is drawn by hand
and is not written by this script.

Requires only the Python standard library.
"""
import csv
import itertools
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Formal contexts
# ---------------------------------------------------------------------------

K1 = {
    'id': 'K1', 'name': 'battery models',
    'M': ['60V', '64V', '72V', 'LiFePO4', 'Li-ion', 'capacity in Ah', 'capacity in kWh',
          'dimensions', 'weight', 'certification', 'unit identifier', 'state of charge',
          'health indicator', 'temperature'],
    'G': ['b1', 'b2', 'b3', 'b4'],
    'label': {'b1': 'SWAP 64 V', 'b2': 'SWAP 72 V', 'b3': 'Volta 401', 'b4': 'Volta Eagle'},
    'eco': {'b1': 'SWAP', 'b2': 'SWAP', 'b3': 'Volta', 'b4': 'Volta'},
    'I': {'b1': 'xx..x?xx?xxxxx',
          'b2': '..x.xxx?xxxxxx',
          'b3': 'x..x.x????xx??',
          'b4': '.x.x.x????????'},
}

K2 = {
    'id': 'K2', 'name': 'station device types',
    'M': ['exchange', 'charging', 'capacity <= 2', 'capacity 3-8', 'status per slot',
          'SoC per slot', 'booking', 'dimensions', 'certification', 'host partner',
          'separate reader', 'colour = process state', 'colour = charge level'],
    'G': ['s1', 's2', 's3', 's4'],
    'label': {'s1': 'SWAP 3-slot', 's2': 'SWAP 8-slot', 's3': 'SWAP Home',
              's4': 'Volta SGB cabinet'},
    'eco': {'s1': 'SWAP', 's2': 'SWAP', 's3': 'SWAP', 's4': 'Volta'},
    'I': {'s1': 'x.x.??xxxx..x',
          's2': 'x..xxxxxxxxx.',
          's3': '.xx...?x?..??',
          's4': 'xx.xxxx??x.??'},
}

K3 = {
    'id': 'K3', 'name': 'service flows',
    'M': ['object transfer', 'energy transfer', 'payment in flow', '15-min limit',
          '6-hour limit', 'borrowed pack', 'ownership retained', 'scan required',
          'membership', 'network enrolment', 'separate reader', 'separate swap record',
          'automatic door', 'same pack returned'],
    'G': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7'],
    'label': {'f1': 'SWAP 3-slot exchange', 'f2': 'SWAP 8-slot exchange',
              'f3': 'SWAP booking', 'f4': 'Volta direct exchange', 'f5': 'Volta booking',
              'f6': 'Volta Tukar Titip', 'f7': 'Volta SCB'},
    'eco': {'f1': 'SWAP', 'f2': 'SWAP', 'f3': 'SWAP',
            'f4': 'Volta', 'f5': 'Volta', 'f6': 'Volta', 'f7': 'Volta'},
    'I': {'f1': 'x..?..???..x?.',
          'f2': 'x..?..???.xx?.',
          'f3': 'x..?..???.?x?.',
          'f4': 'x.....?xxx.?x.',
          'f5': 'x.xx..?xxx.?x.',
          'f6': 'x.xxxxxxxx.??x',
          'f7': '.x.xx.xxx..??x'},
}

# K4 is retained for completeness. Its lattice is the full Boolean lattice on
# three objects (8 concepts under both readings), so no attribute implication
# holds and the lattice adds nothing to the specification table. It is reported
# in the paper as a table rather than as a lattice.
K4 = {
    'id': 'K4', 'name': 'vehicle models',
    'M': ['1500 W', '2500 W', 'one pack', 'two packs', 'weight <= 150 kg', 'weight > 150 kg',
          'double disc brake', 'keyless without NFC', 'keyless with NFC', 'vehicle identifier'],
    'G': ['v1', 'v2', 'v3'],
    'label': {'v1': 'Smoot De Sultan', 'v2': 'Volta 401', 'v3': 'Volta Eagle'},
    'eco': {'v1': 'SWAP', 'v2': 'Volta', 'v3': 'Volta'},
    'I': {'v1': '.x??x..??x',
          'v2': 'x..x.x.x.x',
          'v3': 'x..xx.x.x?'},
}

CONTEXTS = [K1, K2, K3, K4]

# Concepts singled out in the discussion; drawn with a highlight ring.
HIGHLIGHT = {
    'K1': [('b1', 'b4')],
    'K2': [('s3', 's4')],
    'K3': [('f1', 'f2', 'f3', 'f4', 'f5', 'f6'), ('f6', 'f7')],
    'K4': [],
}

# ---------------------------------------------------------------------------
# Formal concept analysis
# ---------------------------------------------------------------------------

def incidence(K, unarticulated_as):
    """Object -> set of attribute indices, for one reading of '?'."""
    out = {}
    for g in K['G']:
        row = K['I'][g]
        if len(row) != len(K['M']):
            raise ValueError('%s/%s: %d cells, expected %d'
                             % (K['id'], g, len(row), len(K['M'])))
        out[g] = {i for i, c in enumerate(row)
                  if c == 'x' or (c == '?' and unarticulated_as)}
    return out


def extents(K, unarticulated_as):
    """All closed object sets, i.e. the extents of the formal concepts."""
    ctx = incidence(K, unarticulated_as)
    everything = set(range(len(K['M'])))
    found = set()
    for size in range(len(K['G']) + 1):
        for A in itertools.combinations(K['G'], size):
            shared = set.intersection(*[ctx[g] for g in A]) if A else everything
            found.add(frozenset(g for g in K['G'] if shared <= ctx[g]))
    return found, ctx


def analyse(K):
    pes, ctx = extents(K, 0)
    opt, _ = extents(K, 1)
    robust = pes & opt
    crossing = [e for e in robust
                if 0 < len(e) < len(K['G']) and len({K['eco'][g] for g in e}) > 1]
    return {'pessimistic': pes, 'optimistic': opt, 'robust': robust,
            'crossing': crossing, 'ctx': ctx}


def structure(K):
    """Hasse diagram of the pessimistic lattice, with reduced labelling."""
    res = analyse(K)
    ctx, pes = res['ctx'], res['pessimistic']
    nodes = sorted(pes, key=lambda e: (len(e), sorted(e)))
    cover = [(a, b) for a in nodes for b in nodes
             if a < b and not any(a < c < b for c in nodes)]
    obj_at, att_at = {}, {}
    for g in K['G']:
        own = frozenset(x for x in K['G'] if ctx[g] <= ctx[x])
        obj_at.setdefault(own, []).append(g)
    for i, m in enumerate(K['M']):
        ext = frozenset(x for x in K['G'] if i in ctx[x])
        if ext in pes:
            att_at.setdefault(ext, []).append(m)
    return nodes, cover, res['robust'], obj_at, att_at


# ---------------------------------------------------------------------------
# Layout and drawing
# ---------------------------------------------------------------------------

def ranks(nodes, cover):
    below = {n: [a for a, b in cover if b == n] for n in nodes}
    r = {n: 0 for n in nodes}
    changed = True
    while changed:
        changed = False
        for n in nodes:
            v = max([r[a] + 1 for a in below[n]], default=0)
            if v != r[n]:
                r[n] = v
                changed = True
    return r


def positions(nodes, cover, r, sweeps=80):
    levels = {}
    for n in nodes:
        levels.setdefault(r[n], []).append(n)
    for k in levels:
        levels[k].sort(key=lambda e: sorted(e))
    pos = {}
    for k, ns in levels.items():
        for i, n in enumerate(ns):
            pos[n] = [i - (len(ns) - 1) / 2.0, k]
    nb = {n: set() for n in nodes}
    for a, b in cover:
        nb[a].add(b)
        nb[b].add(a)
    for _ in range(sweeps):                       # barycentre crossing reduction
        for k in sorted(levels):
            ns = levels[k]
            if len(ns) < 2:
                continue
            ns.sort(key=lambda n: (sum(pos[m][0] for m in nb[n]) / len(nb[n]))
                    if nb[n] else pos[n][0])
            for i, n in enumerate(ns):
                pos[n][0] = i - (len(ns) - 1) / 2.0
    return pos


def draw_panel(K, title, cx, ytop, dx, dy, out):
    nodes, cover, robust, obj_at, att_at = structure(K)
    r = ranks(nodes, cover)
    pos = positions(nodes, cover, r)
    height = max(r.values())
    rings = [frozenset(s) for s in HIGHLIGHT[K['id']]]
    place = lambda n: (cx + pos[n][0] * dx, ytop + (height - pos[n][1]) * dy)

    out.append('<text x="%.0f" y="%.0f" class="ttl">%s</text>' % (cx - 3.6 * dx, ytop - 34, title))
    for a, b in cover:
        xa, ya = place(a)
        xb, yb = place(b)
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="edge"/>'
                   % (xa, ya, xb, yb))
    for n in nodes:
        x, y = place(n)
        if n in rings:
            out.append('<circle cx="%.1f" cy="%.1f" r="10.5" class="ring"/>' % (x, y))
        out.append('<circle cx="%.1f" cy="%.1f" r="5" class="%s"/>'
                   % (x, y, 'robust' if n in robust else 'dependent'))
        for i, a in enumerate(reversed(att_at.get(n, []))):
            out.append('<text x="%.1f" y="%.1f" class="att">%s</text>' % (x, y - 12 - i * 11.5, a))
        for i, g in enumerate(obj_at.get(n, [])):
            klass = 'swap' if K['eco'][g] == 'SWAP' else 'volta'
            out.append('<text x="%.1f" y="%.1f" class="obj %s">%s</text>'
                       % (x, y + 19 + i * 11.5, klass, K['label'][g]))


STYLE = ('<style>'
         '.edge{stroke:#a3abb5;stroke-width:1.1}'
         '.robust{fill:#1f2933;stroke:#1f2933;stroke-width:1.2}'
         '.dependent{fill:#ffffff;stroke:#8b95a1;stroke-width:1.4;stroke-dasharray:2.6 2}'
         '.ring{fill:none;stroke:#c8452e;stroke-width:1.7}'
         'text{font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
         '.att{font-size:10px;fill:#1a4b8c;text-anchor:middle;font-weight:600}'
         '.obj{font-size:10px;text-anchor:middle}'
         '.swap{fill:#166534}.volta{fill:#9a3412}'
         '.ttl{font-size:13px;font-weight:700;fill:#111111}'
         '.cap{font-size:10px;fill:#3d444d}'
         '</style>')


def draw_figure(path):
    out = [STYLE]
    draw_panel(K1, '(a)  K1 — battery models', 300, 120, 150, 92, out)
    draw_panel(K2, '(b)  K2 — station device types', 940, 120, 150, 92, out)
    draw_panel(K3, '(c)  K3 — service flows', 600, 610, 175, 88, out)

    out.append('<g transform="translate(1000,600)">')
    out.append('<circle cx="8" cy="0" r="5" class="robust"/>'
               '<text x="22" y="3.5" class="cap">robust concept — present under both readings</text>')
    out.append('<circle cx="8" cy="21" r="5" class="dependent"/>'
               '<text x="22" y="24.5" class="cap">assumption-dependent — pessimistic reading only</text>')
    out.append('<circle cx="8" cy="42" r="8" class="ring"/>'
               '<text x="22" y="45.5" class="cap">concept discussed in the text</text>')
    out.append('<text x="0" y="68" class="cap">'
               '<tspan class="swap" style="font-weight:700">SWAP Energy</tspan><tspan> · </tspan>'
               '<tspan class="volta" style="font-weight:700">Volta</tspan><tspan> · </tspan>'
               '<tspan style="fill:#1a4b8c;font-weight:700">attribute</tspan></text>')
    out.append('</g>')

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 1000" '
           'width="1500" height="1000"><rect width="1500" height="1000" fill="#ffffff"/>'
           + ''.join(out) + '</svg>')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(svg)


def write_contexts(directory):
    for K in CONTEXTS:
        path = os.path.join(directory, 'context_%s.csv' % K['id'])
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['object', 'label', 'ecosystem'] + K['M'])
            for g in K['G']:
                w.writerow([g, K['label'][g], K['eco'][g]] + list(K['I'][g]))


# ---------------------------------------------------------------------------

def main():
    print('Formal concept analysis — BSDO')
    print()
    print('%-22s %6s %6s %6s %8s %9s' % ('context', '|G|', '|M|', 'pess.', 'optim.', 'robust'))
    print('-' * 64)
    for K in CONTEXTS:
        r = analyse(K)
        print('%-22s %6d %6d %6d %8d %9d   crossing: %d'
              % ('%s %s' % (K['id'], K['name']), len(K['G']), len(K['M']),
                 len(r['pessimistic']), len(r['optimistic']), len(r['robust']),
                 len(r['crossing'])))
    print()
    print('"crossing" counts robust, non-trivial concepts whose extent contains')
    print('objects from both ecosystems. A count above zero is what shows that the')
    print('lattice does not simply reproduce the boundary between the two operators.')
    print()
    write_contexts(HERE)
    # A screen rendering of the same structure, under its own name. The figure
    # published with the paper, fig_lattice_K1_K3.svg, is drawn by hand and is
    # checked by verify_figure.py rather than generated -- nothing here writes
    # to it.
    fig = os.path.join(HERE, 'fig_lattice_screen.svg')
    draw_figure(fig)
    print('written: context_K1.csv, context_K2.csv, context_K3.csv, context_K4.csv')
    print('written: %s' % os.path.basename(fig))


if __name__ == '__main__':
    main()
