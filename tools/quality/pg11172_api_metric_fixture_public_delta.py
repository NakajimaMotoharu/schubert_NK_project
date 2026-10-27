"""Save explicit public metric proof delta, excluding held names before content access."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11172-api-metric-fixture-public-delta-v1'
scan.BEFORE='07d17bd95'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg111',
    'tools/quality/architecture/SuppliedMetricFixtureJunitLauncher.java')
if __name__=='__main__':
    scan.main()
