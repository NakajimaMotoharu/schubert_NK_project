"""Public one-Test semantic oracle delta and exact independent Protocol launcher only."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '6f24d3738'
    stage.PREFIXES += ('tools/quality/pg107','tools/quality/architecture/ProtocolSemanticJunitLauncher.java')
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10754-protocol-semantic-source-public-delta-v1'
    stage.main()
