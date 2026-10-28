"""Exact public delta only; held names are excluded before file access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13454-current-printable-public-v1'
scan.BEFORE = '88fb9859551bd6b184dfa5f0b7d55397a0180194'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg134','tools/quality/f03_current_ascii_literals.py','tools/quality/f03_literal_batch_preflight_v4.py')

if __name__ == '__main__':
    scan.main()
