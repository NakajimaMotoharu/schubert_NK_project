"""Explicit public current delta, held paths excluded before any content read."""
import pg12706_scenario_writer_public as scan

scan.OUT=scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12782-api-duration-public-v1'
scan.BEFORE='2984aba2e30b19c26fb73b54dc576fd8474b67d8'
scan.PREFIXES=(*scan.PREFIXES,'tools/quality/architecture/ApiDurationFixtureJunitLauncher.java','tools/quality/architecture/ApiDurationFixtureArtifactCoverageMeasure.java')

if __name__=='__main__':
    scan.main()
