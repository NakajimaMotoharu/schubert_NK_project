"""Three newly specified direct semantic cases; immutable values only, no external resources."""
import scoped_prometheus_host as run

if __name__ == '__main__':
    run.SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
    run.COMPILE = run.host.W / 'pg9660-pagination-six-compile-v1'
    run.COMPILE_SHA = 'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c'
    run.SLOT = run.host.W / 'pg9662-pagination-boundary-host-v1'
    run.OUT = run.host.ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9662-pagination-boundary-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/PaginationBoundaryJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadPaginationBoundaryTest.java'
    run.COUNTS = {'PayloadPaginationBoundaryTest': 3}
    run.EXTRA_TEST_SOURCES = ()
    run.TEST_SOURCE_OVERRIDES = {}
    run.SESSION_ID = 'PG9662-PROTOCOL-PAGINATION-BOUNDARY'
    run.FIXTURES = {}
    assert run.host.sha(run.NEW_TEST) == '6f8038c90b3854656b38c6b641a0c6ae4f5d0db66a12c562edf594e52c9c739d'
    assert run.host.sha(run.HELPER) == '7d6d3c2db29cc63cd49425ca01b4d639ce262b9653f5a19fffa4703d09731b52'
    run.main()
