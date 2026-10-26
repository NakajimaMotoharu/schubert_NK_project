"""Public import-only source delta; no held-path content access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '219ca9f51'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10696-graph-import-source-public-delta-v1'
    stage.main()
