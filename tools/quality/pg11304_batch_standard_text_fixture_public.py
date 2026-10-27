"""Save explicit public Batch standard-to-text six-Test PG/PT evidence without held reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11304-batch-standard-text-fixture-public-v1'
scan.BEFORE='a5d11e79d'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112','tools/quality/pg113',
    'tools/quality/architecture/BatchStandardTextFixtureJunitLauncher.java')
if __name__=='__main__':
    scan.main()
