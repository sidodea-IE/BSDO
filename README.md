# BSDO — Battery Swap Domain Ontology

An OWL 2 DL domain ontology for battery swap ecosystems for electric two-wheelers.

BSDO models the entities that battery swapping requires and that charging-oriented vocabularies do
not provide: a battery pack as a persistent object with an identity of its own, its changing
location over time, the separation of ownership from physical custody, and the exchange of a pack as
a transfer of an object rather than a transfer of energy.

The class hierarchy is derived from Formal Concept Analysis over artefacts observed in two
independently operated ecosystems, so that every class can be traced back to the facts that motivated
it. Each class and property records that derivation in its annotations.

## Files

| File | Contents |
|---|---|
| `bsdo.ttl` · `bsdo.owl` | Terminology (TBox): classes, properties, alignment targets |
| `bsdo-abox.ttl` · `bsdo-abox.owl` | Population (ABox): individuals for the two ecosystems |
| `bsdo-cq8-test.ttl` · `bsdo-cq8-test.owl` | Cross-ecosystem incompatibility test scenario |
| `bsdo-merged.ttl` · `bsdo-merged.owl` | Terminology and population in one file |
| `bsdo-merged-cq8.ttl` · `bsdo-merged-cq8.owl` | The above, plus the incompatibility test |
| `catalog-v001.xml` | Maps ontology IRIs to local files so imports resolve offline |

Every file is provided in Turtle and in RDF/XML. The two serialisations of each file were checked to
carry identical triple sets.

## Getting started

Open `bsdo-merged.owl` in an OWL editor such as Protégé. It combines terminology and population in a
single document, so no imports need to be resolved over the network.

To work with terminology and population as separate documents, open `bsdo.ttl` or `bsdo-abox.ttl`
from a directory that also contains `catalog-v001.xml`; Protégé reads the catalogue automatically and
resolves the import locally.

## The incompatibility test

`bsdo-cq8-test.ttl` asserts that a lithium iron phosphate pack from one ecosystem is accepted by a
handling device of the other ecosystem that admits lithium-ion packs only.

Loading it together with the terminology and population **is expected to make the knowledge base
inconsistent.** That is the point of the file: incompatibility between ecosystems is detected as
logical unsatisfiability rather than as an empty query result, which distinguishes a genuine conflict
from missing data under the open-world assumption.

For ordinary work, use `bsdo-merged.owl`, which is consistent. To reproduce the test, load
`bsdo-merged-cq8.owl` and run a reasoner; it should report an inconsistency.

## Reasoning

The merged ontology classifies as consistent and coherent. No class is subsumed by `owl:Nothing` and
no individual is unsatisfiable, with all inference types precomputed.

| Metric | Value |
|---|---|
| Axioms | 613 |
| Logical axioms | 256 |
| Classes | 36 |
| Object properties | 19 |
| Data properties | 13 |
| Individuals | 48 |

## Alignment

BSDO aligns to the EMMO **domain-battery** and **domain-electrochemistry** modules, which form the
vocabulary layer that the BattINFO application ontology profiles.

Alignment is **by reference rather than by import**: referenced classes are declared locally with
labels and pointers to their defining module. Importing the modules in full would introduce several
thousand classes to obtain two subsumption relations and two quantity references, at substantial cost
to reasoning time and none to expressiveness.

## Multilingual labels

Preferred labels are English. Terms used by the observed ecosystems are retained as
`skos:altLabel` in Indonesian rather than translated away, because several of them have no
equivalent in the other ecosystem — the absence of a shared term is part of what the ontology
records.

## Data statement

The population is derived from operator applications, public operator websites, and manufacturer
documentation. All identifiers are pseudonymised: personal names, vehicle registration numbers,
chassis and engine numbers, battery serial numbers, and geographic coordinates. What is retained is
the *pattern* of each identifier scheme, because the mutual uninterpretability of the two schemes is
itself a finding. No raw capture is distributed in this repository.

Where a value derives from promotional or demonstration material rather than live operation, the
individual's annotation says so. The field structure such material exposes is treated as evidence;
the values are not treated as measurements.

## Namespace

Entity IRIs are minted under `https://w3id.org/bsdo#`, with `owl:versionIRI`
`https://w3id.org/bsdo/0.2.0`.

## Status

Version 0.2.0-draft. The artefact accompanies a manuscript under preparation; classes, properties
and identifiers may change before the first stable release.

## Licence

Creative Commons Attribution 4.0 International (CC BY 4.0). See `LICENSE`.
