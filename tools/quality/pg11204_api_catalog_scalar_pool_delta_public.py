"""Public three-source ID-delta save, excluding held names before content access."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11204-api-catalog-scalar-pool-delta-public-v1'
scan.BEFORE='e4f2cef65'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112')
if __name__=='__main__':
    scan.main()
