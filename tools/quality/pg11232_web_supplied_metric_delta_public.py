"""Save explicit public current Web supplied metric ID delta without held-file reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11232-web-supplied-metric-delta-public-v1'
scan.BEFORE='fe3dcd48a'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112')
if __name__=='__main__':
    scan.main()
