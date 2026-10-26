"""Explicit public Web batch artifacts only; held paths excluded by original selector before reading."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'ce5dded70ecd53d2202fc4b07517d8f8d85a1f01'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10860-web-view-public-delta-v1'
    stage.PREFIXES += ('tools/quality/pg108',
        'tools/quality/architecture/WebViewFixtureBatchJunitLauncher.java',
        'tools/quality/architecture/WebViewArtifactCoverageMeasure.java')
    stage.main()
