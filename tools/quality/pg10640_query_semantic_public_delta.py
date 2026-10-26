"""Explicit query semantic constant public delta with pre-read held exclusion."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '4758ba3ba'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10640-query-semantic-public-delta-v1'
    stage.main()
