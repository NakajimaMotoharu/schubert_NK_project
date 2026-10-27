"""Concrete GC fixture defects and poison-oracle public review only; no held content reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11438-gc-fake-comparable-review-public-v1'
scan.BEFORE='f9ef70449'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg114')
if __name__=='__main__':
    scan.main()
