"""Exact public text delta; held names excluded before content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13494-positioned-literal-public-v1'
scan.BEFORE = '48783a999f43dec0a36b334a88c0a53f374aa88a'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg134','tools/quality/f03_positioned_ascii_literals.py','tools/quality/f03_positioned_ascii_literals_v2.py','tools/quality/f03_literal_batch_preflight_v5.py')

if __name__ == '__main__':
    scan.main()
