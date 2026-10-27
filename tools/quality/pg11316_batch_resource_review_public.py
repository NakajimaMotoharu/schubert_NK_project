"""Save explicit public31 resource contract review and open guard defect; no held reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11316-batch-resource-review-public-v1'
scan.BEFORE='0c06a4d49'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113')
if __name__=='__main__':
    scan.main()
