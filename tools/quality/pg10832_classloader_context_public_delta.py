"""Public single-rule ClassLoader current-source context only."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '808d879a9'
    stage.PREFIXES += ('tools/quality/pg108',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10832-classloader-context-public-delta-v1'
    stage.main()
