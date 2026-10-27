"""Concrete caller audit and pre-fix defects; explicit public delta, no held reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11374-source-constructor-owner-public-v1'
scan.BEFORE='883b7789b'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113')
if __name__=='__main__':
    scan.main()
