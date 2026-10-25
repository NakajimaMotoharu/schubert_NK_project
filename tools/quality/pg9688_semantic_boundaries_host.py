"""Current semantic single-run boundary closure candidate, fixed fifteen cases only."""
import scoped_prometheus_host as run

if __name__ == '__main__':
    run.SOURCE = '0002706babad635c5ca7ade76cdbaee134ace432'
    run.COMPILE = run.host.W / 'pg9686-semantic-direct-six-compile-v1'
    run.COMPILE_SHA = '890012b6561777b4f8d19e1f4118f4fe11d26cf2eeedd005f24f60c33f2356cc'
    run.SLOT = run.host.W / 'pg9688-semantic-boundaries-host-v1'
    run.OUT = run.host.ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9688-semantic-boundaries-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/SemanticBoundaryCompletionJunitLauncher.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout'
    run.NEW_TEST = run.TEST_ROOT / 'SemanticDirectBoundaryTest.java'
    run.COUNTS = {'PayloadPaginationBoundaryTest':3,'PayloadSemanticValidatorTest':8,'PayloadTypeCatalogTest':1,'SemanticDirectBoundaryTest':3}
    run.EXTRA_TEST_SOURCES = (run.TEST_ROOT / 'IndependentNamedFieldOracle.java',)
    run.TEST_SOURCE_OVERRIDES = {}
    run.SESSION_ID = 'PG9688-PROTOCOL-SEMANTIC-BOUNDARIES'
    run.FIXTURES = {}
    run.main()
