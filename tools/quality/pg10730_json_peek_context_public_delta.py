"""Explicit public parser-context source evidence delta only; held paths excluded."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'c7f69f072'
    stage.PREFIXES += ('tools/quality/pg107',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10730-json-peek-context-public-delta-v1'
    stage.main()
