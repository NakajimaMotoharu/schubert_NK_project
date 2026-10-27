"""Public changed-source/tool/evidence scan; held paths excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12738-alert-threshold-public-v1'
scan.BEFORE='c4054da1a0ea380781ed39817ad7af67e6a3a182'
scan.PREFIXES=(*scan.PREFIXES,'tools/quality/architecture/AlertThresholdJunitLauncher.java','tools/quality/architecture/AlertThresholdArtifactCoverageMeasure.java')

if __name__=='__main__':
    scan.main()
