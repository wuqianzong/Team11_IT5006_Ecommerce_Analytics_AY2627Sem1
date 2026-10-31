# Notice to Benson: B-CR-42, the Milestone 2 report (2026-10-30)

Henry, as delegated lead (LEAD_DELEGATION.md), decided M2-D1 to D6 of `m2_rework_handshake.md`. Each step is its own
commit and can be reverted alone.

1. **B-G-14.** The register may read A's s01 and s04–s08 outputs at tag e5-A-frozen, sha256 checked, read only, as
   B-G-11 and B-G-13 do for s03 and s02.
2. **A's interpretation (M2-N1).** `deliverables/m2_report/a_interpretation/make_a_interpretation.py` loads A's frozen
   T1 bundles, checks they re-predict T1 (max difference 2e-14), and computes coefficients and permutation importance
   on A's test rows with B9.5's method, scoring, repeats and seed. No fit, no choice, T1 not rerun. Run
   20261030T010520Z; the register reads it as `M2A/<file>` through `verify_manifest_source`, which generalises
   B-CR-41's check. M2-N2 (error analysis by state) and M2-N3 (A-only test charts) were not built: the report shows
   test results as tables.
3. **Where it lives.** `deliverables/m2_report/`, register prefix `M2.`; review doc
   https://claude.ai/artifact/JySsRqxpAETeEN7rAj8dUj. The deliverables audit was not extended to it (M2-D5: fill/check).

Supersedes `m2_rework_handshake.md` and D1, D4–D7 of the combined handshake. D2 (deck v2 chart map) and D3 (chart
renders) are still open.
