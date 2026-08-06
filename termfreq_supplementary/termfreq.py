"""Lexical scan supporting Section 2 of the BSDO paper.

Counts vocabulary for two BSOR dimensions across the four ontologies that
Table 2 records as assessed from their publications, under two term lists
(narrow / broad) declared in terms.json before counting.

Every occurrence matched only by the broad list is printed as a KWIC line, so
a reader can judge for themselves whether it is domain usage or an authorial
verb. That is the whole point: the gap between the two columns is where a
lexical scan can mislead, and it is shown rather than resolved silently.

    python termfreq.py            # table + KWIC
    python termfreq.py --quiet    # table only

Requires only the standard library.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
CFG = json.loads((HERE / "terms.json").read_text(encoding="utf-8"))

ROOT = (HERE / CFG["corpus"]["root"]).resolve()
DOCS = CFG["corpus"]["documents"]
CATS = CFG["categories"]


def load(fn):
    p = ROOT / fn
    if not p.exists():
        sys.exit(f"missing corpus file: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def hits(text, terms):
    """{term: [match objects]} for whole-word, case-insensitive matches."""
    return {t: list(re.finditer(rf"\b{re.escape(t)}\b", text, re.I)) for t in terms}


def total(h):
    return sum(len(v) for v in h.values())


def kwic(text, m, width=68):
    flat = re.sub(r"\s+", " ", text)
    # re-locate in the whitespace-collapsed string for readable output
    frag = re.sub(r"\s+", " ", text[m.start():m.end()])
    i = flat.find(frag, max(0, m.start() - 200))
    if i < 0:
        i = m.start()
    a, b = max(0, i - width), min(len(flat), i + len(frag) + width)
    return f"...{flat[a:b]}..."


def main():
    quiet = "--quiet" in sys.argv
    rows = []

    for name, fn in DOCS.items():
        text = load(fn)
        row = {"artefact": name, "words": len(text.split())}
        broad_only = {}

        for cat, spec in CATS.items():
            narrow = spec["narrow"]
            extra = spec["broad_extra"]
            hn = hits(text, narrow)
            he = hits(text, extra)
            row[f"{cat}__narrow"] = total(hn)
            row[f"{cat}__broad"] = total(hn) + total(he)
            broad_only[cat] = he

        rows.append(row)

        if not quiet:
            any_extra = any(total(h) for h in broad_only.values())
            if any_extra:
                print(f"\n{'=' * 74}\nKWIC — broad-only occurrences in {name}\n{'=' * 74}")
                for cat, he in broad_only.items():
                    for term, ms in he.items():
                        for m in ms:
                            print(f"  [{cat}/{term}] {kwic(text, m)}")

    print(f"\n{'=' * 74}\nRESULTS\n{'=' * 74}")
    hdr = f"{'artefact':<26}{'words':>7}"
    for cat in CATS:
        hdr += f"{cat + ' N':>26}{'B':>6}"
    print(hdr)
    for r in rows:
        line = f"{r['artefact']:<26}{r['words']:>7}"
        for cat in CATS:
            line += f"{r[f'{cat}__narrow']:>26}{r[f'{cat}__broad']:>6}"
        print(line)
    print("\nN = narrow list, B = broad list. See terms.json for both.")


if __name__ == "__main__":
    main()
