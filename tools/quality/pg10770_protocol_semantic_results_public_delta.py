"""Public semantic results and exact metadata reader; held names excluded before content."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '1f20074cdf'
    stage.PREFIXES += ('tools/quality/pg107','tools/quality/architecture/ProtocolSemanticCoverageMeasure.java')
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10770-protocol-semantic-results-public-delta-v1'
    stage.main()
