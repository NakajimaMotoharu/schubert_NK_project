"""Explicit public diagnostic-constant source delta; excludes held paths before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '87d519843'
    stage.PREFIXES += ('tools/quality/pg107',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10712-graph-constants-source-public-delta-v1'
    stage.main()
