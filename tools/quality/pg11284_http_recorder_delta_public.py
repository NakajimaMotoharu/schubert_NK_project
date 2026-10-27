"""Save explicit public HTTP recorder finding-ID delta only; no held reads or replay."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11284-http-recorder-delta-public-v1'
scan.BEFORE='1347fe775'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112')
if __name__=='__main__':
    scan.main()
