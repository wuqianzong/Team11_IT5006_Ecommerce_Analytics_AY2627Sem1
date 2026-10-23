"""Pipeline B's own code (G-79, CR-054). Only what B adds: population rules, history features,
stage runners and B's output writer. Everything inherited is imported read-only from e5lib, and
env.assert_a_frozen() refuses to run when A's code differs from tag e5-A-frozen."""
