"""Public exact-source API readonly-owner review delta; held paths excluded before reading."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'c675cda20'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10938-api-ro-prior-public-v1'
    stage.PREFIXES += ('tools/quality/pg109',)
    stage.main()
