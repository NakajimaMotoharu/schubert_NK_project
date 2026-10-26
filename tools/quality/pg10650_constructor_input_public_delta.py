"""Explicit public literal-input review delta, held paths excluded before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '6d582f5f1'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10650-constructor-input-public-delta-v1'
    stage.main()
