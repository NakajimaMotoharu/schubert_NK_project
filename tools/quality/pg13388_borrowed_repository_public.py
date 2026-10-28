"""Exact public text delta only; held names excluded before content access; no Product execution."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13388-borrowed-repository-public-v1'
scan.BEFORE = '8fa5dd207c44f037e36723a062b953a96a67b76c'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg133','tools/quality/architecture/BorrowedRepositoryJunitLauncher.java')
if __name__ == '__main__':scan.main()
