"""Explicit business Test/tool/document delta, excluding held names before reading content."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as scan

if __name__ == '__main__':
    scan.OUT = data.BASE/'PG13068-time-header-public-v1'
    scan.BEFORE = '643f843ab9d6a1a548e8040adcfd9cfadb4fc221'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg130','tools/quality/architecture/TimeHeaderBoundaryJunitLauncher.java','tools/quality/architecture/TimeHeaderBoundaryArtifactCoverageMeasure.java')
    scan.main()
