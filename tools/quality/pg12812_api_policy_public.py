"""Explicit public text delta scan; held tools excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12812-api-policy-public-v1'
scan.BEFORE='802dc3bd1e0bf0ee45fc092fd66e4e60db85e5d4'
scan.PREFIXES=(*scan.PREFIXES,'tools/quality/pg128','tools/quality/architecture/ApiApprovedClosureJunitLauncher.java','tools/quality/architecture/ApiApprovedClosureArtifactCoverageMeasure.java')

if __name__=='__main__':
    scan.main()
