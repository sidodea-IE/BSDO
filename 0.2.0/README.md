# BSDO 0.2.0 — frozen release

This directory holds release 0.2.0 exactly as published, and is the target of
the version identifier `https://w3id.org/bsdo/0.2.0`.

**Do not edit these files.** A version identifier has to keep resolving to the
release it names, so that an ontology or a dataset which declared an import of
`https://w3id.org/bsdo/0.2.0` still resolves to what it was written against
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

Archived with a DOI at <https://doi.org/10.5281/zenodo.21683493>.

Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).
