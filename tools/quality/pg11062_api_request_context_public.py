"""Explicit public source-context and small-delta save only; held paths excluded before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '33e6c4c7c'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11062-api-request-context-public-v1'
    stage.PREFIXES += ('tools/quality/pg110',)
    stage.main()
