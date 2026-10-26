"""Public current F03 delta only, excluding held paths before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'f7fa8ed86'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10972-current-form-public-v1'
    stage.PREFIXES += ('tools/quality/pg109',)
    stage.main()
