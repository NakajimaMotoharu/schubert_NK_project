"""Explicit current Web F03 delta and fail-closed lint control evidence save."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '266a2e698'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11126-current-web-pure-value-public-v1'
    stage.PREFIXES += ('tools/quality/pg111',)
    stage.main()
