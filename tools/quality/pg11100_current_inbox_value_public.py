"""Explicit current Inbox F03 metadata delta save; held paths excluded before read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '87c4456b7'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11100-current-inbox-value-public-v1'
    stage.PREFIXES += ('tools/quality/pg110','tools/quality/pg111',)
    stage.main()
