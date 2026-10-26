"""Public current-F03 delta only; held paths excluded by original selector before file reads."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '5928d47c73a6b7ce5744944a8372a3990d5defc0'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10914-current-f03-delta-public-v1'
    stage.PREFIXES += ('tools/quality/pg109',)
    stage.main()
