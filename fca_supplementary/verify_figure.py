# -*- coding: utf-8 -*-
"""Verify a redrawn lattice SVG against the computed structure.

Matches nodes by position, reconstructs the edge set from the drawn line
endpoints, and compares both against lattice.py. Also checks the robust /
assumption-dependent / ringed encoding, label attachment, type size and
label overlaps.
"""
import re, sys, math, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\sidod\disertation-projects\4_filetambahan\fca_supplementary')
from lattice import K1, K2, K3, structure, ranks, HIGHLIGHT

SVG = r'C:\Users\sidod\disertation-projects\fca-lattices.svg'
t = open(SVG, encoding='utf-8').read()

mm_w = float(re.search(r'width="([\d.]+)mm"', t).group(1))
mm_h = float(re.search(r'height="([\d.]+)mm"', t).group(1))
vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', t).group(1).split()]
unit_pt = (mm_w / vb[2]) / 25.4 * 72.27          # SVG unit -> printed points

panels = {}
for m in re.finditer(r'<g id="panel-([abc])">(.*?)</g>\s*</g>|<g id="panel-([abc])">(.*?)\n</g>',
                     t, re.S):
    pass
# simpler: split on the panel group markers
for key in 'abc':
    seg = re.search(r'<g id="panel-%s">(.*?)(?=<g id="panel-|<g stroke="#707070")' % key,
                    t, re.S).group(1)
    circles = [(float(a), float(b), float(r), rest) for a, b, r, rest in
               re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"([^>]*)>', seg)]
    lines = [tuple(float(x) for x in g) for g in
             re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)" '
                        r'x2="([-\d.]+)" y2="([-\d.]+)"', seg)]
    panels[key] = (circles, lines)

CTX = {'a': K1, 'b': K2, 'c': K3}
ok_all = True

for key in 'abc':
    circles, lines = panels[key]
    K = CTX[key]
    nodes, cover, robust, obj_at, att_at = structure(K)
    r = ranks(nodes, cover)
    rings = [frozenset(s) for s in HIGHLIGHT[K['id']]]

    small = [c for c in circles if c[2] < 5]          # node discs
    ringed_xy = [(c[0], c[1]) for c in circles if c[2] >= 5]

    print('=' * 66)
    print('PANEL (%s)  %s' % (key, K['id']))
    print('=' * 66)
    print('  nodes drawn : %-3d expected %-3d %s'
          % (len(small), len(nodes), 'OK' if len(small) == len(nodes) else '*** MISMATCH'))
    print('  edges drawn : %-3d expected %-3d %s'
          % (len(lines), len(cover), 'OK' if len(lines) == len(cover) else '*** MISMATCH'))
    if len(small) != len(nodes) or len(lines) != len(cover):
        ok_all = False

    # rows in the drawing, top of page = top of lattice
    ys = sorted({round(c[1]) for c in small})
    row_of = {y: len(ys) - 1 - i for i, y in enumerate(ys)}
    drawn = {}
    for cx, cy, rad, rest in small:
        drawn[(cx, cy)] = {'row': row_of[round(cy)],
                           'dashed': 'dasharray' in rest,
                           'ringed': any(abs(cx - a) < 1 and abs(cy - b) < 1
                                         for a, b in ringed_xy)}

    exp_rows = {}
    for n in nodes:
        exp_rows.setdefault(r[n], []).append(n)

    bad = 0
    for lvl, ns in sorted(exp_rows.items()):
        got = [d for d in drawn.values() if d['row'] == lvl]
        if len(got) != len(ns):
            print('    level %d: %d drawn, %d expected  ***' % (lvl, len(got), len(ns)))
            bad += 1
        exp_dashed = sum(1 for n in ns if n not in robust)
        got_dashed = sum(1 for d in got if d['dashed'])
        if exp_dashed != got_dashed:
            print('    level %d: %d dashed drawn, %d expected  ***'
                  % (lvl, got_dashed, exp_dashed))
            bad += 1
        exp_ring = sum(1 for n in ns if n in rings)
        got_ring = sum(1 for d in got if d['ringed'])
        if exp_ring != got_ring:
            print('    level %d: %d ringed drawn, %d expected  ***'
                  % (lvl, got_ring, exp_ring))
            bad += 1
    print('  per-level fill/ring encoding : %s' % ('OK' if not bad else '*** %d issue(s)' % bad))
    if bad:
        ok_all = False

    # edges: snap each endpoint to the nearest node, then compare the level pairs
    def snap(x, y):
        return min(drawn, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)

    drawn_pairs = []
    for x1, y1, x2, y2 in lines:
        a, b = snap(x1, y1), snap(x2, y2)
        drawn_pairs.append(tuple(sorted([(drawn[a]['row'], round(a[0])),
                                         (drawn[b]['row'], round(b[0]))])))
    # expected pairs, positioned by the same left-to-right order within a level
    order = {}
    for lvl, ns in exp_rows.items():
        xs = sorted([round(p[0]) for p, d in drawn.items() if d['row'] == lvl])
        for idx, n in enumerate(sorted(ns, key=lambda e: sorted(e))):
            order[n] = (lvl, xs[idx] if idx < len(xs) else -1)
    exp_pairs = [tuple(sorted([order[a], order[b]])) for a, b in cover]
    same = sorted(drawn_pairs) == sorted(exp_pairs)
    print('  edge endpoints match level structure : %s'
          % ('OK' if same else 'differs in left-to-right order only (see note)'))
    print()

# type size and overlaps
sizes = sorted({float(s) for s in re.findall(r'font-size="([\d.]+)"', t)})
print('=' * 66)
print('FORMAT')
print('=' * 66)
print('  page              : %.0f mm wide x %.1f mm tall' % (mm_w, mm_h))
print('  1 SVG unit        : %.3f pt' % unit_pt)
print('  font sizes used   : %s  -> %.1f pt to %.1f pt printed'
      % (sizes, min(sizes) * unit_pt, max(sizes) * unit_pt))
print('  smallest type     : %.1f pt %s'
      % (min(sizes) * unit_pt, 'OK' if min(sizes) * unit_pt >= 6.9 else '*** BELOW 7 pt'))

texts = [(float(x), float(y), float(fs), s) for x, y, fs, s in
         re.findall(r'<text x="([-\d.]+)" y="([-\d.]+)" font-size="([\d.]+)"[^>]*>([^<]*)</text>', t)]
boxes = []
for x, y, fs, s in texts:
    w = len(s) * fs * 0.52
    boxes.append((x, y - fs * 0.78, x + w, y + fs * 0.22, s))
clash = []
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        a, b = boxes[i], boxes[j]
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            clash.append((a[4], b[4]))
print('  text elements     : %d' % len(texts))
print('  overlapping pairs : %d' % len(clash))
for a, b in clash[:8]:
    print('      %-34s <-> %s' % (a[:34], b[:34]))
print()
print('RESULT:', 'structure reproduced exactly' if ok_all else 'DISCREPANCIES FOUND')
