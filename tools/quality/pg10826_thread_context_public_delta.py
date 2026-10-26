"""Public current-source architecture/rule context only; exact held exclusion first."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '1491595eb'
    stage.PREFIXES += ('tools/quality/pg108',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10826-thread-context-public-delta-v1'
    stage.main()
