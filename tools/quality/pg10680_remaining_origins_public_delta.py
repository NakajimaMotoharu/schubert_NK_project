"""Exact public delta after source-only origin review; excludes held paths before reading."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '3364db231'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10680-remaining-origins-public-delta-v1'
    stage.main()
