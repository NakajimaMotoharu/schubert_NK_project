"""Save explicit public HTTP recorder fixture/owner PG/PT evidence, held names excluded first."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11278-http-recorder-fixture-public-v1'
scan.BEFORE='f0e0fad4b'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112',
    'tools/quality/architecture/HttpRecorderFixtureJunitLauncher.java')
if __name__=='__main__':
    scan.main()
