"""Publish explicit API request delta, excluding held paths before content access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '183644b09'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11052-api-request-public-v1'
    stage.PREFIXES += ('tools/quality/pg110','tools/quality/architecture/ApiRequestFixtureJunitLauncher.java','tools/quality/architecture/ApiRequestArtifactCoverageMeasure.java')
    stage.main()
