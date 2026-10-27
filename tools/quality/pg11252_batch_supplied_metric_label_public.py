"""Save explicit public Batch supplied metric label PG/PT evidence without held-file access."""
import pg10606_fixed_error_public_delta as scan
scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11252-batch-supplied-metric-label-public-v1'
scan.BEFORE='0ea02b2e2212673ba65753a7547f44cd3d9b08fa'
scan.PREFIXES=('documents/','evidence/01_PT/','src/','tools/quality/pg112',
    'tools/quality/architecture/BatchSuppliedMetricLabelFixtureJunitLauncher.java',
    'tools/quality/architecture/BatchSuppliedMetricArtifactCoverageMeasure.java')
if __name__=='__main__':
    scan.main()
