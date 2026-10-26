"""Explicit qualified-constructor input review delta, held names removed before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '70cbff07e'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10656-qualified-input-public-delta-v1'
    stage.main()
