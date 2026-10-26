"""Public source-derived F03 index and exact metadata tools only; held exclusions maintained."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'caa6d9427'
    stage.PREFIXES += ('tools/quality/pg108',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10838-f03-index-public-delta-v1'
    stage.main()
