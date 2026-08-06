# BSDO 0.3.0 — frozen release

This directory holds release 0.3.0 exactly as published, and is the target of
the version identifier `https://w3id.org/bsdo/0.3.0`.

**Do not edit these files.** A version identifier has to keep resolving to the
release it names, so that an ontology or a dataset which declared an import of
`https://w3id.org/bsdo/0.3.0` still resolves to what it was written against
after later releases change the files in the parent directory.

Edits belong in the parent directory, which always carries the current release.
A new release adds a new directory beside this one; it does not modify this one.

| File | Contents |
|---|---|
| `bsdo.ttl` · `bsdo.owl` | Terminology (TBox) |
| `bsdo-abox.ttl` · `bsdo-abox.owl` | Population (ABox) |
| `bsdo-cq8-test.ttl` · `bsdo-cq8-test.owl` | Cross-ecosystem incompatibility test |
| `bsdo-merged.ttl` · `bsdo-merged.owl` | Terminology and population in one file |
| `bsdo-merged-cq8.ttl` · `bsdo-merged-cq8.owl` | The above, plus the incompatibility test |
| `catalog-v001.xml` | Maps ontology IRIs to these files for offline import resolution |

## What changed since 0.2.0

`owl:priorVersion` on the terminology points back to
`https://w3id.org/bsdo/0.2.0`, so the release chain is machine-traceable.

- **Class derivation is now recorded in the artefact.** Every class carries a
  `derivationPath` annotation stating which of four provenances it has:
  `lattice` (a formal concept robust under both readings of the unarticulated
  cells, with its context, extent and intent named), `composed`, `reuse`, or
  `structural`. The path from an observed fact to a class can be reconstructed
  without access to the authors.
- **Chemistry alignment extended.** The lithium iron phosphate value of the
  chemistry partition is linked to the EMMO chemical-substance module. The
  generic cell family declared by the other ecosystem has no substance-level
  counterpart and is therefore left unaligned; that asymmetry is a result, not
  an omission.
- **Population provenance.** Individuals carry a source annotation recording
  what each value was read from, and the identifier-scheme individuals record
  the observed pattern of each scheme.

The version number moves the minor component rather than the patch component
because the signature gained a term: `derivationPath` did not exist in 0.2.0.

Archived with a DOI at <https://doi.org/10.5281/zenodo.21683493>.

Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).
