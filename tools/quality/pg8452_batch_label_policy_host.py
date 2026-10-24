"""Original Batch closed labels14/1, not writer/endpoint or old PT replay."""
import scoped_prometheus_host as run

SOURCE = 'cc6638e7a185901e9102f4bcb1db2d92a6330135'
COMPILE = run.host.W / 'pg8450-batch-label-policy-six-compile-v1'
COMPILE_SHA = 'ec739b4d0b388391f0d6af721c45c9ad52b295ec3f9adadadc1c40d793d8e463'
COUNTS = {'BatchMetricLabelPolicyTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8452-batch-label-policy-host-v1'
    run.OUT = run.host.BASE / 'PG8452-batch-label-policy-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/BatchMetricLabelJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricLabelPolicyTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8452-BATCH-LABEL-POLICY'
    run.FIXTURES = {}
    run.main()

