"""Public current ID-delta metadata only; exclude held names before reads."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11178-api-metric-delta-public-v1'
scan.BEFORE='46579c165'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg111')
if __name__=='__main__':
    scan.main()
