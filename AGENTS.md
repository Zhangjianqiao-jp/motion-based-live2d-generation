# Project Instructions

- `RESEARCH_SPEC.md` is the authoritative research specification.
- Do not silently change the research question; surface conflicts between the specification and code.
- Do not fabricate experimental results, dataset facts, citations, or prior work.
- Every research discussion and design decision must cite and list authoritative paper references.
- Work baseline-first and do not over-engineer before the smallest falsifiable experiment runs.
- Static RGB is the inference input unless the specification explicitly says otherwise.
- Teacher-side rig information is training-only and cannot be used at inference.
- Motion dependency is not equivalent to displacement similarity or motion magnitude.
- Surface unresolved scientific decisions as `DECISION REQUIRED` before implementing them.
- Every experiment must state its hypothesis and preserve reproducibility through explicit configs, seeds, splits, and machine-readable artifacts where applicable.
- Existing code may be modified when it conflicts with the current specification.
- Do not reintroduce ideas deprecated in `RESEARCH_SPEC.md` without explicit justification.
