"""Exact public source/evidence delta only; held names excluded before every content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13414-remaining-literal-public-v1'
scan.BEFORE = 'c73b0218882998c1aa42751344eaf560a5c71a02'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg134')

if __name__ == '__main__':
    scan.main()
