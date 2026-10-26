"""Public Main owner-null and immutable-index references; held paths excluded before content read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '53a68aa91'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10926-main-owner-route-public-v1'
    stage.PREFIXES += ('tools/quality/pg109',)
    stage.main()
