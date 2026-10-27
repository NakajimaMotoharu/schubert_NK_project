"""Explicit API/Web source guard PG/PT public delta only; held names excluded before content."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11362-api-web-source-guard-public-v1'
scan.BEFORE='625250bd9d00156c2cec627b9c65519e2a3ddd09'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg113',
    'tools/quality/architecture/StandardSourcePairJunitLauncher.java',
    'tools/quality/architecture/StandardSourcePairArtifactCoverageMeasure.java')
if __name__=='__main__':
    scan.main()
