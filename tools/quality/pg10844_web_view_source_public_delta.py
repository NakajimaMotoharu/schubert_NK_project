"""Public eight-Test same-value Web fixture PG source; held exclusions first."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'ce5dded70'
    stage.PREFIXES += ('tools/quality/pg108',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10844-web-view-source-public-delta-v1'
    stage.main()
