"""Current payload literal ID delta public scope only; held names excluded before content."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11432-current-api-web-payload-literal-public-v1'
scan.BEFORE='a82f72bec'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg114')
if __name__=='__main__':
    scan.main()
