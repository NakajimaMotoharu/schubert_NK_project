"""Save explicit public Batch source guard PG/PT and expanded YKT boundary; no held reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11336-batch-source-guard-public-v1'
scan.BEFORE='58a19debd'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113',
    'tools/quality/architecture/BatchSourceGuardJunitLauncher.java')
if __name__=='__main__':
    scan.main()
