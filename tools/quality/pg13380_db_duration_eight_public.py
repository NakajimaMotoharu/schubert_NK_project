"""Exact public delta scan; held names excluded before content access; no Product execution."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13380-db-duration-eight-public-v1'
scan.BEFORE = '13e9a8f1b2083e82b569ae19e44c46750adb9c1b'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg133','tools/quality/architecture/DbDurationCollectorJunitLauncher.java','tools/quality/architecture/CoverageSessionIdentity.java')
if __name__ == '__main__':scan.main()
