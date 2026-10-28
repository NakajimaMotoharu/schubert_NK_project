"""Explicit same delta; correct BASE owner, no original failed entry mutation."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG12990-query-binding-public-v1'
    scan.BEFORE = '78aa0f6cae9c35bf1bd17b1e5c19a22d3326a80d'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg129','tools/quality/architecture/QueryBindingJunitLauncher.java','tools/quality/architecture/QueryBindingArtifactCoverageMeasure.java')
    scan.main()
