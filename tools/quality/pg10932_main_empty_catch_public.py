"""Public Main comment-only catch local-review artifacts; held files remain unread."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'c6f0ca3d0'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10932-main-empty-catch-public-v1'
    stage.PREFIXES += ('tools/quality/pg109',)
    stage.main()
