"""Exact public text delta only; held names excluded before reading."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13434-cleanup-value-public-v1'
scan.BEFORE = 'f7c7241025a3ef6235568385132dd0e7207daff1'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg134','tools/quality/architecture/CleanupCurrentValueJunitLauncher.java')

if __name__ == '__main__':
    scan.main()
