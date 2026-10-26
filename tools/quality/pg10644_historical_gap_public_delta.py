"""Explicit historical-gap metadata delta; held paths excluded before content reads."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '1e23e1a94'
    stage.PREFIXES = (*stage.PREFIXES,'tools/quality/architecture/UserQueryHistoricalGapMetadata.java')
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10644-historical-gap-public-delta-v1'
    stage.main()
