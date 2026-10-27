"""Save explicit public current Batch standard/text finding-ID set delta only."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11310-batch-standard-text-delta-public-v1'
scan.BEFORE='faa5d310e'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113')
if __name__=='__main__':
    scan.main()
