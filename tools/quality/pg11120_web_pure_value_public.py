"""Explicit pure Web value Test delta and source-bound evidence save; no held file read."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '6e9a2bbbb'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11120-web-pure-value-public-v1'
    stage.PREFIXES += ('tools/quality/pg111','tools/quality/architecture/WebPureValueJunitLauncher.java')
    stage.main()
