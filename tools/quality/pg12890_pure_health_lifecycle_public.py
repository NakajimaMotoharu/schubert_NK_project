"""Explicit public text delta; held tools excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12890-pure-health-lifecycle-public-v1'
scan.BEFORE = '1597f73541421bdbd15bb57db3b1b6a61f581b8a'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/pg128',
    'tools/quality/architecture/PureHealthLifecycleJunitLauncher.java',
    'tools/quality/architecture/PureHealthLifecycleArtifactCoverageMeasure.java')

if __name__ == '__main__':
    scan.main()
