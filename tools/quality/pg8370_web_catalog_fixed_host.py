"""BUG1700 new catalog source, original14/1; old pre-repair PASS is not transferred."""
import pg8364_web_catalog_host as previous

SOURCE = 'e5f0ae543177ccd5f399e58d8588092868466f8e'
COMPILE = previous.run.host.W / 'pg8368-web-catalog-fixed-six-compile-v1'
COMPILE_SHA = '0081b454a19a70df71693d96bb1e8d5dccf5ebad339ea34ad25c8fe343bde28f'
COUNTS = previous.COUNTS
FIXTURE, FIXTURE_SHA = previous.FIXTURE, previous.FIXTURE_SHA

if __name__ == '__main__':
    run = previous.run
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8370-web-catalog-fixed-host-v1'
    run.OUT = run.host.BASE / 'PG8370-web-catalog-fixed-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebMetricCatalogJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricCatalogTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8370-WEB-CATALOG'
    run.FIXTURES = {FIXTURE: FIXTURE_SHA}
    run.main()
