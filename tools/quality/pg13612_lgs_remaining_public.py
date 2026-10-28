"""Exact public current remaining-branch delta; excludes both held paths before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13612-lgs-remaining-public-v1'
scan.BEFORE = '8d455cc6a3f4240a1aaeb5ee74e46efd9e8e7dac'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/pg135', 'tools/quality/pg136', 'tools/quality/f03_lgs_remaining_')

if __name__ == '__main__':
    scan.main()
