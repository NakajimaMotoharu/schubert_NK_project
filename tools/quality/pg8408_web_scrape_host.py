"""Original pure mode/scrape14/1, old approved encoder96 not replayed for confirmation."""
import scoped_prometheus_host as run

SOURCE = '8c8a8c51a166948a03510bda521a6e3930e88fa2'
COMPILE = run.host.W / 'pg8406-web-scrape-six-compile-v1'
COMPILE_SHA = '2176ef1e0b5b1e70d7f4bdd28ea797075846e10dd0a31a58b641c9de9de3789f'
COUNTS = {'WebMetricScrapeTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8408-web-scrape-host-v1'
    run.OUT = run.host.BASE / 'PG8408-web-scrape-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebMetricScrapeJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricScrapeTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8408-WEB-SCRAPE'
    run.FIXTURES = {}
    run.main()
