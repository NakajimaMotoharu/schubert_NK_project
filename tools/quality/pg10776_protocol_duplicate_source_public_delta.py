"""Public eleven-Test fixture batch only; no held-file content access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '6943eee8e'
    stage.PREFIXES += ('tools/quality/pg107',)
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10776-protocol-duplicate-source-public-delta-v1'
    stage.main()
