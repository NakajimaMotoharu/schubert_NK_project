"""Public Protocol component quality results and one exact metadata-only reader."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = 'e73e95589'
    stage.PREFIXES += ('tools/quality/pg108','tools/quality/architecture/ProtocolArtifactCoverageMeasure.java')
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10820-protocol-quality-results-public-delta-v1'
    stage.main()
