"""Save current Batch label ID delta and tool correction explicit public files only."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11258-batch-metric-label-delta-public-v1'
scan.BEFORE='234ed0b43'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112')
if __name__=='__main__':
    scan.main()
