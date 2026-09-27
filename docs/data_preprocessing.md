# Asset preprocessing

Run from the repository root with Python 3.6 or newer. No third-party packages are required.

```bash
python3 scripts/inspect_live2d_data.py \
  --source /home/pj26000152/ku60000936/Downloads \
  --output /home/pj26000152/ku60000936/live2d_data_audit_new
python3 -m unittest discover -s tests -p 'test_inspect_live2d_data.py' -v
```

The output directory must be new and outside the source tree. Originals are read
only. Exit status: 0 for completed static checks, 1 for an execution error,
2 for scan issues or invalid model references. A failed execution can leave a
partial output directory with `run.json` marked `running`; use a new directory
for a retry. No runtime loading, rendering or archive extraction is performed.

| Output | Contents |
| --- | --- |
| `inventory.jsonl` | Relevant asset/document paths, sizes and SHA-256 hashes |
| `manifest.jsonl` | Model references, static check errors, unverified identity/rights fields |
| `duplicates.json` | Identical MOC files and identical referenced bundles |
| `documents.jsonl` | Documentation candidates for manual provenance/license review |
| `archives.jsonl` | Archive inventory; integrity and extraction are not tested |
| `scan_issues.jsonl` | Skipped links, unreadable paths and filesystem errors |
| `summary.json`, `REPORT.md` | Measured inventory and remaining work |
| `run.json` | Command, source root, Python version, script hash and completion status |

The scanner excludes macOS metadata, Git internals and symlinks. It inventories
recognized asset extensions and document files; it is not a full filesystem backup.
Static checks require nonempty referenced files and object-valued valid JSON;
they do not decode textures, validate full Cubism schemas or execute MOC binaries.
Optional unsupported file extensions are reported as unsupported references.

Bundle identity includes raw model JSON and role-indexed resource hashes, including
textures. This is conservative exact-content grouping, not semantic deduplication.
Same MOC hashes do not establish the same complete asset or independent characters.
No files are deleted. Archive provenance, PSD/editor pairing, licensing and character
identity require review. No automatic character splits or motion labels are produced.

This is a data inventory utility, not a scientific experiment. Before teacher data
generation, resolve the specification's canonical state, intervention, physics and
motion-dependency label decisions. Student inference remains RGB-only.

Research context: Hu et al. (2017), *Learning to Predict Part Mobility from a Single
Static Snapshot*, ACM TOG, https://doi.org/10.1145/3130800.3130811.
The paper uses 3D part structure; this utility neither implements its method nor
establishes the single-RGB research hypothesis.
