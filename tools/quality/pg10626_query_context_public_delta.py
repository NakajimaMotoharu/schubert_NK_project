"""Exact public context-review delta; held files excluded by existing selector."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '28bd6fe99'
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10626-query-context-public-delta-v1'
    stage.main()
