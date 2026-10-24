"""Original WEBCAT14/1, immutable independent route fixture; no historical PT replay."""
import scoped_prometheus_host as run

SOURCE = '7ca3acb10533696798a368321032b4bbaeb7fd86'
COMPILE = run.host.W / 'pg8362-web-catalog-six-compile-v1'
COMPILE_SHA = '51c75e43da20b8089a81fbc24dc7e4d5d797e4f8d511225ab0c68db2b14f7e96'
COUNTS = {'WebMetricCatalogTest': 14}
FIXTURE = 'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
FIXTURE_SHA = '1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8364-web-catalog-host-v1'
    run.OUT = run.host.BASE / 'PG8364-web-catalog-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebMetricCatalogJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricCatalogTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8364-WEB-CATALOG'
    run.FIXTURES = {FIXTURE: FIXTURE_SHA}
    run.main()
