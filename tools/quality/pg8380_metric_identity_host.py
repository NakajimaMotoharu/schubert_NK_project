"""First existing-source approved-name contract4; no Main repair or historical PT replay."""
import scoped_prometheus_host as run

SOURCE = 'e5f0ae543177ccd5f399e58d8588092868466f8e'
COMPILE = run.host.W / 'pg8368-web-catalog-fixed-six-compile-v1'
COMPILE_SHA = '0081b454a19a70df71693d96bb1e8d5dccf5ebad339ea34ad25c8fe343bde28f'
COUNTS = {'MetricIdentitySnapshotContractTest': 4}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8380-metric-identity-host-v1'
    run.OUT = run.host.BASE / 'PG8380-metric-identity-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/MetricIdentitySnapshotJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/MetricIdentitySnapshotContractTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8380-METRIC-IDENTITY'
    run.FIXTURES = {}
    run.main()
