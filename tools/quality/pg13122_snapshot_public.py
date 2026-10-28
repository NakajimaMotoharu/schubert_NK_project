"""Public snapshot delta only, held paths subtracted before content reads."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13122-snapshot-max-public-v1'
    scan.BEFORE = '94c0a5fbffabd102cd4a0174c737c954404badde'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg130','tools/quality/pg131',
        'tools/quality/architecture/SnapshotMaximumJunitLauncher.java',
        'tools/quality/architecture/SnapshotMaximumArtifactCoverageMeasure.java')
    scan.main()
