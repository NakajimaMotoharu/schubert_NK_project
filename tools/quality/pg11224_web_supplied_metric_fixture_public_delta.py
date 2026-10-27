"""Save explicit public Web metric proof/correction delta; held names excluded before reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11224-web-supplied-metric-fixture-public-delta-v1'
scan.BEFORE='0fb1a78e2'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112',
    'tools/quality/architecture/WebSuppliedMetricFixtureJunitLauncher.java')
if __name__=='__main__':
    scan.main()
