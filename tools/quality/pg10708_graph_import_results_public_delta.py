"""Public import-only qualification results, held names excluded before content reads."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '0a7ff6571'
    stage.PREFIXES += ('tools/quality/pg107',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10708-graph-import-results-public-delta-v1'
    stage.main()
