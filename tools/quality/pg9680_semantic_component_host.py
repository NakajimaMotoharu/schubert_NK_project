"""Necessary single-run semantic component qualification; no normal/full/VM replay."""
import scoped_prometheus_host as run

if __name__ == '__main__':
    run.SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
    run.COMPILE = run.host.W / 'pg9660-pagination-six-compile-v1'
    run.COMPILE_SHA = 'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c'
    run.SLOT = run.host.W / 'pg9680-semantic-component-host-v1'
    run.OUT = run.host.ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9680-semantic-component-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/SemanticComponentJunitLauncher.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout'
    run.NEW_TEST = run.TEST_ROOT / 'PayloadPaginationBoundaryTest.java'
    run.COUNTS = {'PayloadPaginationBoundaryTest':3,'PayloadSemanticValidatorTest':8}
    run.EXTRA_TEST_SOURCES = tuple(run.TEST_ROOT / p for p in ('PayloadTypeCatalogTest.java','IndependentNamedFieldOracle.java'))
    run.TEST_SOURCE_OVERRIDES = {}
    run.SESSION_ID = 'PG9680-PROTOCOL-SEMANTIC-COMPONENT'
    run.FIXTURES = {}
    run.main()
