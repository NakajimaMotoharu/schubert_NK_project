"""Public metadata delta only, no held content access or product replay."""
import pg10606_fixed_error_public_delta as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11152-web-presentation-delta-public-v1'
scan.BEFORE='f5c1e8f3c'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg111')

if __name__=='__main__':
    scan.main()
