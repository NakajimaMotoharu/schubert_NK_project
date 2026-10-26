"""Explicit fixture-origin public review delta; pre-read held exclusions maintained."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '203c46fdd'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10668-fixture-input-public-delta-v1'
    stage.main()
