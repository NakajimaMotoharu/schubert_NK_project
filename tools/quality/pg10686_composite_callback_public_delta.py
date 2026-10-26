"""Explicit public source-review delta only; held paths excluded before content access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '65016d7ac'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10686-composite-callback-public-delta-v1'
    stage.main()
