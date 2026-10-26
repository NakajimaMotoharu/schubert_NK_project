"""Explicit Inbox pure Test and source-bound evidence save; no held file read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'ebea8774d'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11094-inbox-lifecycle-public-v1'
    stage.PREFIXES += ('tools/quality/pg110','tools/quality/architecture/InboxValueFixtureJunitLauncher.java')
    stage.main()
