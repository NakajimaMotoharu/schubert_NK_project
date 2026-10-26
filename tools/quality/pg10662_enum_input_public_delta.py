"""Explicit direct-enum public review delta, held names excluded before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'f176ef285'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10662-enum-input-public-delta-v1'
    stage.main()
