"""Explicit public text delta scan, held tools excluded before reads."""
import pg12706_scenario_writer_public as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12866-monitor-sequence-public-v1'
scan.BEFORE='d8ceb9b93'
scan.PREFIXES=(*scan.PREFIXES,'tools/quality/pg128','tools/quality/architecture/MonitoringSequenceJunitLauncher.java','tools/quality/architecture/MonitoringSequenceArtifactCoverageMeasure.java')

if __name__=='__main__':
    scan.main()
