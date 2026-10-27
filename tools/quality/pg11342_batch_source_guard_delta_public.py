"""Save current active-ID Batch guard delta without duplicate prior corrections or held reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11342-batch-source-guard-delta-public-v1'
scan.BEFORE='2bc69c619'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113')
if __name__=='__main__':
    scan.main()
