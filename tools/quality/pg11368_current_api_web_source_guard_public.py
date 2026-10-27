"""Current actual API/Web static-ID delta public files only; no held reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11368-current-api-web-source-guard-public-v1'
scan.BEFORE='813df177e'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113')
if __name__=='__main__':
    scan.main()
