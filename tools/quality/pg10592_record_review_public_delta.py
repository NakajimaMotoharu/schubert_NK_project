"""Save only explicit public delta; exclude held paths before content access."""
import pg10586_constructor_bindings_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '995d7b0b7'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10592-record-review-public-delta-v1'
    stage.main()
