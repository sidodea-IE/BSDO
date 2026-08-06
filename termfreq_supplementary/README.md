# Lexical scan — supplementary material for Section 2

Supports the vocabulary observations in Sections 2.2 and 2.3 of *BSDO: A domain
ontology for battery swap station and electric motorcycle swappable battery
ecosystems*.

```bash
python termfreq.py            # results table + KWIC for every broad-only hit
python termfreq.py --quiet    # results table only
```

Standard library only. No arguments, no configuration: the term lists and the
corpus are declared in `terms.json`.

---

## What this is, and what it is not

It is a **supporting indicator**, not evidence. An ontology can model a relation
without ever naming it, so a word count cannot establish that a construct is
absent. The structural argument in Section 2.3 — that the plug-in charging frame
leaves nothing for an ownership relation or a location history to attach to —
stands independently of every number below.

What the scan does establish is narrower and still useful: where the vocabulary
*does* appear, it can be inspected, and inspecting it turns out to matter more
than counting it (see "Ownership" below).

## Method

- **Corpus.** Publication text, taken from the extracted `.pdf.md` of each paper
  in `2_source_article/`. **Not** ontology files. The scan covers exactly the
  four artefacts that Table 2 records as assessed *from their publications*.
  Artefacts assessed from their ontology files are excluded: mixing prose with
  serialised RDF in a single count would make the figure uninterpretable.
- **Matching.** Whole word, case-insensitive, no stemming.
- **Two term lists per category**, fixed in `terms.json` before counting.
  - *Narrow* — words denoting the concept itself.
  - *Broad* — narrow plus inflected and verbal forms.

  Both are reported. Every occurrence matched **only** by the broad list is
  printed as a KWIC line, so a reader can adjudicate each one without rerunning
  anything. The gap between the two columns is where a lexical scan can mislead;
  it is shown rather than resolved silently.

## Results

| Artefact | words | Identity / traceability (D1) | | Ownership / custody (D4) | |
|---|---:|---:|---:|---:|---:|
| | | narrow | broad | narrow | broad |
| Battery Production Ontology | 16,435 | **144** | 167 | 1 | 3 |
| EVO | 4,864 | **0** | 0 | 2 | 3 |
| ChargingStationOntology | 4,637 | **0** | 9 | 1 | 2 |
| OntoSoC | 10,371 | **0** | 3 | 0 | 0 |

### Identity and traceability

BPO, narrow list: `traceability` 107 · `provenance` 18 · `trace` 13 ·
`identifier` 3 · `traceable` 3. The words `identity` and `identifiers` do not
occur; the count rests on `traceability` and `identifier`.

The other three artefacts return **zero on the narrow list**. Their broad-only
occurrences were inspected and none concerns the identity of a unit:

- ChargingStationOntology (9) — authorial or procedural throughout: *"the first
  step was to identify the scope of our ontology"*, *"the authors identify MaaS
  as one of the most important … technologies"*, *"E-Mobility and eMaaS have
  been identified among the most promising"*. One case, *"Once the available CPs
  are identified"*, concerns locating charge points, not identifying them
  persistently.
- OntoSoC (3) — battery **parameter** estimation, e.g. *"identify the parameters
  of the battery pack"*, plus one occurrence inside a cited reference title.
- EVO (0) — the word family does not appear at all, in either list.

In BPO, by contrast, `identification` is largely genuine domain usage
(*"Identification assigns a unique identifier to each trace object"*, *"physical
identification layer"*, *"cell-level identification"*). Excluding it therefore
**understates** BPO while leaving the three zeros untouched, which is why the
narrow figure is the one quoted in the paper.

### Ownership and custody

Here the counts are small enough that inspection replaces counting, and the
result is sharper than any number.

`custody`, `custodian`, and `possession` **do not occur in any of the four
publications.** The narrow list matches four times in total, and in no case does
it denote ownership of a battery:

| Artefact | Term | Context | What it denotes |
|---|---|---|---|
| ChargingStationOntology | `owners` | "stakeholders, e.g., EV owners, Charging Stations, grid suppliers" | stakeholder category |
| EVO | `owners` | "industry stakeholders e.g., EV owners, Charging Stations…" | stakeholder category |
| EVO | `owner` | "As an EV owner, I want to find charging stations…" | competency-question persona |
| BPO | `ownership` | "schema:Organization captures ownership and operational control of a facility" | ownership of a **facility** |

Three name a person who owns a vehicle, in prose rather than as a modelled
relation. The fourth is a modelled ownership relation, but its range is a
production facility, not a battery.

Broad-only matches in this category are noise and are retained precisely so that
they can be seen to be noise: `own` is the possessive (*"its own
characteristics"*, *"our own terms"*), and `title` matches bibliography fields
(*"Publication Title:"*). Polysemous terms of this kind are the reason the broad
list is reported separately rather than merged.

## Limits

1. Publication text is a proxy for an artefact. A paper may under-describe the
   ontology it presents.
2. Counts are not normalised by document length. BPO is roughly three times the
   length of the two shortest papers; the zeros are unaffected by this, but the
   144 should not be compared to the others as a rate.
3. No synonym expansion. A vocabulary expressing custody through some other word
   family would not be detected — which is the first limitation, restated, and
   the reason the scan is reported as an indicator only.
