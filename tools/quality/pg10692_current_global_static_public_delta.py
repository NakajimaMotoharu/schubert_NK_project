"""Explicit public full-static evidence delta, held paths excluded before access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '20437fa25'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10692-current-global-static-public-delta-v1'
    stage.main()
