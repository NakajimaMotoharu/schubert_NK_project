"""Public five-source Protocol Test quality corrections only."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'f11ef987e'
    stage.PREFIXES += ('tools/quality/pg107',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10798-protocol-residual-source-public-delta-v1'
    stage.main()
