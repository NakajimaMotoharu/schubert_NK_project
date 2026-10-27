"""Current full-payload static-ID join public delta only; held names excluded before content."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11400-current-full-payload-guard-public-v1'
scan.BEFORE='3a3988639'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113','tools/quality/pg114')
if __name__=='__main__':
    scan.main()
