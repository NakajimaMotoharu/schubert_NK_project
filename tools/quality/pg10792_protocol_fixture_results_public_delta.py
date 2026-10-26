"""Public complete Protocol fixture batch results and exact two helpers only."""
import pg10606_fixed_error_public_delta as stage

if __name__ == '__main__':
    stage.BEFORE = '5cc74a2e4'
    stage.PREFIXES += ('tools/quality/pg107',
        'tools/quality/architecture/ProtocolFixtureBatchJunitLauncher.java',
        'tools/quality/architecture/ProtocolFixtureBatchCoverageMeasure.java')
    stage.OUT = stage.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10792-protocol-fixture-results-public-delta-v1'
    stage.main()
