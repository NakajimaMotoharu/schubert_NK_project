"""Final concrete source-owner scope closure public delta; no held reads or product replay."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11406-source-owner-guard-final-public-v1'
scan.BEFORE='a000e128c'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg114')
if __name__=='__main__':
    scan.main()
