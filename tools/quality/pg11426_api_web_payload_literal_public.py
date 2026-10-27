"""Explicit eight-literal same-oracle PG/PT public delta; held names excluded before content."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11426-api-web-payload-literal-public-v1'
scan.BEFORE='2ecfe29cd'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg114',
    'tools/quality/architecture/PayloadLiteralFixtureJunitLauncher.java',
    'tools/quality/architecture/PayloadLiteralFixtureArtifactCoverageMeasure.java')
if __name__=='__main__':
    scan.main()
