# Steering — Testing Standards

## Levels

1. Unit: brief schema validation, finding-record validation (evidence rule),
   report generation from stored records. Run with pytest.
2. Pipeline: full run on the sample pack, scored against
   `sample-pack/ANSWER_KEY.json` (planted vs caught, timestamp ±1s).
3. Acceptance (banked v1, BUILD_SPEC_v1.md §9 — all must hold, measured):
   1. Wrong-logo plant caught; evidence frame within 1s of the stated time.
   2. Missing-scene plant caught, identified by brief scene id.
   3. Black-frame plant caught with measured duration stated.
   4. Clean control video produces zero blocker findings.
   5. Every finding opens its evidence view with a real extracted frame.
   6. PDF and JSON reports export and agree with on-screen decisions.
   7. Full run on the 90-second sample completes in under 2 minutes.
   8. A fresh clone runs the sample end to end from its own README.

## Rules

- Tests run on save (hook: `.kiro/hooks/run-tests-on-save`).
- No test may pass on a fixture the code under test generated in the same
  run. The sample pack is generated once by `scripts/make_sample_pack.py`
  and committed; tests read it, they do not regenerate it.
- A failing acceptance criterion blocks filing. There is no "known failure"
  lane for v1.
- Every fix lands with the test that would have caught the defect.
- Run logs are saved under `runs/` (gitignored) and quoted in review rounds.
