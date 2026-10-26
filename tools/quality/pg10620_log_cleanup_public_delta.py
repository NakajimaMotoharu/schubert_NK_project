"""Explicit same-value literal public delta; held names excluded before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'bfd74f2e6'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10620-log-cleanup-public-delta-v1'
    stage.main()
