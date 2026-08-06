# Formal Concept Analysis — supplementary material

Everything needed to reproduce the concept lattices reported in the paper, and the figure that
accompanies them.

## Files

| File | Contents |
|---|---|
| `lattice.py` | Formal contexts, concept computation. **Standard library only** |
| `context_K1.csv` … `context_K4.csv` | The four formal contexts in machine-readable form |
| **`fig_lattice_K1_K3.svg`** · **`.pdf`** | **The figure published with the paper.** Drawn by hand; no script writes to it |
| `verify_figure.py` | Checks that published figure against the computed structure |
| `convert_figure.py` | SVG to PDF with fonts embedded. The output stem follows the input |
| `fig_lattice_screen.svg` | Screen rendering written by `lattice.py`. A working view, not the published figure |
| `make_print_figure.py` | An independent rendering from the same data. Requires matplotlib |
| `fig_lattice_reference.pdf` · `.eps` · `.png` | Output of that rendering |

### Why there is more than one rendering

The published figure is drawn by hand, because a hand-drawn layout reads better
than anything a script produced here. That creates an obvious risk: a drawing
made by hand can quietly disagree with the data it claims to show.

`verify_figure.py` closes that gap. It parses the published SVG, matches every
node by position, reconstructs the edge set from the drawn line endpoints, and
compares node count, edge count, the robust/assumption-dependent encoding and
the ringed concepts against what `lattice.py` computes. It also reports the
smallest type size in printed points and any overlapping labels.

`make_print_figure.py` is kept because it renders the same lattices from the
contexts by running one script. Between them, one figure is legible and the
other is reproducible, and the first is checked against the second's source.

`lattice.py` emits a third rendering, `fig_lattice_screen.svg`, as a by-product
of running the analysis. It is a working view of the same structure under its
own name, so that running the analysis cannot overwrite the published figure.
Nothing downstream reads it.

## Reproducing

```
python lattice.py
```

Recomputes every concept from the contexts, prints the verification table below, rewrites the four
CSV files, and writes the screen rendering `fig_lattice_screen.svg`. No arguments, **no
dependencies** — a bare Python install is enough, which is the point: verifying the analysis should
not require setting up an environment.

It does **not** touch `fig_lattice_K1_K3.svg`. That figure is drawn by hand and is checked by
`verify_figure.py`, not generated — which is what makes the check worth running.

```
python make_print_figure.py
```

Regenerates the publication figure in PDF, EPS and PNG. This step needs matplotlib, which is why it
is kept in a separate script.

The print renderer measures every label after layout and reports any pair whose rendered boxes
intersect, then resolves the remaining collisions by mirroring labels to the other side of their
node. It exits reporting zero collisions; if a future edit to the contexts introduces one, the script
says so rather than leaving it to be found in proof.

## Cell notation

| Symbol | Meaning |
|---|---|
| `x` | the attribute applies, directly observed |
| `.` | **absent** — the attribute genuinely does not apply |
| `?` | **unarticulated** — not exposed by the source, but possibly present |

The distinction between *absent* and *unarticulated* follows Fu (2016). Recording 0 for something
that may exist but was never articulated is an inference rather than an observation, and a lattice
built on such cells makes claims the data does not support.

Across the four contexts, 61 of 236 cells (26%) are unarticulated. That proportion is itself
reportable: it measures how much of the domain the available interfaces leave unstated.

## Two readings, and what counts as a result

Because a quarter of the cells are unarticulated, a single lattice would hide the uncertainty. Two
lattices are computed per context:

- **pessimistic** — `?` read as 0
- **optimistic** — `?` read as 1

A concept whose extent occurs in **both** is **robust**. Only robust concepts were used to derive
classes in the ontology. Concepts occurring in one variant only are **assumption-dependent** and are
reported as such rather than built upon.

## Verification table

| Context | \|G\| | \|M\| | Pessimistic | Optimistic | Robust | Robust and crossing |
|---|---:|---:|---:|---:|---:|---:|
| K1 battery models | 4 | 14 | 13 | 10 | 10 | 2 |
| K2 station device types | 4 | 13 | 12 | 13 | 10 | 3 |
| K3 service flows | 7 | 14 | 14 | 11 | 8 | 1 |
| K4 vehicle models | 3 | 10 | 8 | 8 | 8 | — |

*Crossing* counts robust, non-trivial concepts whose extent contains objects from **both**
ecosystems. Every one of K1–K3 has at least one. This is the non-degeneracy check: had the lattices
simply reproduced the boundary between the two operators, the count would be zero and the analysis
would have discovered nothing that was not put in by hand.

**K4 is degenerate.** Eight concepts over three objects under both readings is the full Boolean
lattice, so no attribute implication holds and the lattice conveys nothing beyond the specification
table. It is reported in the paper as a table, and no lattice is drawn for it.

## What these lattices do and do not show

They are small: 8–14 concepts over 3–7 objects. They do **not** discover hidden structure, and the
paper does not claim they do. What they establish is:

1. **Traceability** — every class in the ontology can be traced back to a robust formal concept, to
   the incidence cells that produced it, and to the observed fact behind each cell.
2. **Reproducibility** — the same context yields the same lattice for anyone who runs it.
3. **A non-degeneracy check that passed** — the structure that survives is functional (object
   transfer versus energy transfer, custody) rather than a restatement of which operator owns what.

The third is the one worth having, and it is a test result rather than an assumption.

## Figure specification

| Property | Value |
|---|---|
| Formats | PDF and EPS (vector), PNG at 600 dpi |
| Width | 190 mm, the publisher's double-column width |
| Height | 216 mm — effectively a full-page figure |
| Smallest type | 6.6 pt |
| Fonts | embedded TrueType (`/FontFile2`); **no Type 3 fonts**, which publishers commonly reject |
| Label collisions | zero, verified by measurement rather than by eye |

Panels are stacked rather than placed side by side. Side-by-side was tried first and abandoned: at
half the column width the space between adjacent concepts is narrower than the widest attribute
label, so labels collide however the spacing is tuned. Stacking is what makes 6.6 pt type legible at
this level of detail.

## Suggested figure caption

> **Fig. X.** Concept lattices for the three artefact families that support lattice analysis:
> (a) battery models, (b) station device types, (c) service flows. Each diagram shows the
> pessimistic lattice under reduced labelling, with attributes above and objects below the concept
> they label. Filled nodes are robust concepts, present under both readings of the unarticulated
> cells; dashed nodes occur under the pessimistic reading only and were not used to derive classes.
> Ringed nodes are discussed in the text. In (a), two packs from different ecosystems share exactly
> one attribute, the 64 V class. In (b), the only attribute joining the two ecosystems' devices is
> charging, while the Volta cabinet also performs exchange. In (c), the concept spanning six of the
> seven flows is robust and contains flows from both ecosystems, whereas the concept collecting the
> three SWAP Energy flows is not robust: the functional boundary survives the sensitivity analysis
> and the operator boundary does not. The vehicle family is omitted; its lattice is the full Boolean
> lattice on three objects and is reported as a specification table instead.

## Publishing

These files are supplementary material for the paper and can also be added to the ontology
repository so that reviewers can audit the derivation without reading the manuscript first:

- https://github.com/sidodea-IE/BSDO
- https://doi.org/10.5281/zenodo.21683493
