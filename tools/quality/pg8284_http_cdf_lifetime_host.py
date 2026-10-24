"""Only three genuinely new ordinary lifetime/CDF cases on unchanged current Main bytes."""
import scoped_prometheus_host as run
import pg8272_summary_encoder_host as original

if __name__ == '__main__':
    run.SOURCE = original.SOURCE
    run.COMPILE = original.COMPILE
    run.COMPILE_SHA = original.COMPILE_SHA
    run.SLOT = run.host.W / 'pg8284-http-cdf-lifetime-host-v1'
    run.OUT = run.host.BASE / 'PG8284-http-cdf-lifetime-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/HttpCdfLifetimeJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/HttpCdfLifetimeContractTest.java'
    run.TEST_ROOT = run.host.ROOT / 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring'
    run.COUNTS = {'HttpCdfLifetimeContractTest': 3}
    run.SESSION_ID = 'PG8284-HTTP-CDF-LIFETIME'
    run.FIXTURES = {}
    run.main()
