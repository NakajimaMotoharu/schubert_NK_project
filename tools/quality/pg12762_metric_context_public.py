"""Current public source/evidence delta; held content is removed before any file access."""
import pg12706_scenario_writer_public as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12762-metric-context-public-v1'
scan.BEFORE='8e9bc79110bce849f6deb3e69638cfc7ac7c3d28'
scan.PREFIXES=(*scan.PREFIXES,'tools/quality/architecture/MetricContextOwnedJunitLauncher.java','tools/quality/architecture/MetricContextOwnedArtifactCoverageMeasure.java')

if __name__=='__main__':
    scan.main()
