"""Current semantic single-run boundary closure candidate, fixed fifteen cases only."""
import scoped_prometheus_host as run

if __name__ == '__main__':
    run.SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
    run.COMPILE = run.host.W / 'pg9694-semantic-direct-fixed-six-compile-v1'
    run.COMPILE_SHA = '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a'
    run.SLOT = run.host.W / 'pg9696-semantic-fixed-host-v1'
    run.OUT = run.host.ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9696-semantic-fixed-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/SemanticBoundaryCompletionJunitLauncher.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout'
    run.NEW_TEST = run.TEST_ROOT / 'SemanticDirectBoundaryTest.java'
    run.COUNTS = {'PayloadPaginationBoundaryTest':3,'PayloadSemanticValidatorTest':8,'PayloadTypeCatalogTest':1,'SemanticDirectBoundaryTest':3}
    run.EXTRA_TEST_SOURCES = (run.TEST_ROOT / 'IndependentNamedFieldOracle.java',)
    run.TEST_SOURCE_OVERRIDES = {}
    run.SESSION_ID = 'PG9696-PROTOCOL-SEMANTIC-FIXED'
    run.FIXTURES = {}
    run.main()
