"""Public current remaining-form delta only; exclude held paths before content access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '3e1b0a25cbf63fc95d7812abb18b9ee7c96991b4'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11032-current-remaining-form-public-v1'
    stage.PREFIXES += ('tools/quality/pg110',)
    stage.main()
