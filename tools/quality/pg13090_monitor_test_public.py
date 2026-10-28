"""Explicit public correction delta; exclude held files before reading any content."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13090-monitor-test-public-v1'
    scan.BEFORE = '5928afadd03539891a93af5f709901c9b1b03e1d'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg130','tools/quality/architecture/MonitorTestNamesJunitLauncher.java','tools/quality/architecture/MonitorTestNamesArtifactCoverageMeasure.java')
    scan.main()
