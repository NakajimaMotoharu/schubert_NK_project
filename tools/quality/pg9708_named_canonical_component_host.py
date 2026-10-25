"""Current named69 canonical component qualification, explicit20 cases/4 classes, no full replay."""
import scoped_prometheus_host as run

if __name__ == '__main__':
    run.SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
    run.COMPILE = run.host.W / 'pg9694-semantic-direct-fixed-six-compile-v1'
    run.COMPILE_SHA = '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a'
    run.SLOT = run.host.W / 'pg9708-named-canonical-component-host-v1'
    run.OUT = run.host.ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9708-named-canonical-component-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/NamedCanonicalComponentJunitLauncher.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout'
    run.NEW_TEST = run.TEST_ROOT / 'SemanticDirectBoundaryTest.java'
    run.COUNTS = {'PayloadPaginationBoundaryTest':3,'PayloadSemanticValidatorTest':8,'PayloadTypeCatalogTest':6,'SemanticDirectBoundaryTest':3}
    run.EXTRA_TEST_SOURCES = (run.TEST_ROOT / 'IndependentNamedFieldOracle.java',)
    run.TEST_SOURCE_OVERRIDES = {}
    run.SESSION_ID = 'PG9708-PROTOCOL-NAMED-CANONICAL'
    run.FIXTURES = {
        'src/schubert-nk-protocol/src/test/resources/protocol/named-accessors-independent.tsv':'27b9a458374f5b9edda50d78fae42ee76dabf15d8d1ecd9c94e56dbab63162d5',
        'src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv':'b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b',
        'src/schubert-nk-protocol/src/test/resources/protocol/named-types-ss323.tsv':'9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76'}
    run.main()
