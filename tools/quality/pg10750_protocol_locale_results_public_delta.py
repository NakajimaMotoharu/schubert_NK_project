"""Public ordinary Protocol locale results and exact metadata readers; no held-file access."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '21d275a74'
    stage.PREFIXES += ('tools/quality/pg107',
        'tools/quality/architecture/ProtocolLocaleCoverageMeasure.java',
        'tools/quality/architecture/ProtocolLocaleCoverageDiagnostic.java',
        'tools/quality/architecture/ProtocolLocaleCoverageMeasureV2.java')
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10750-protocol-locale-results-public-delta-v1'
    stage.main()
