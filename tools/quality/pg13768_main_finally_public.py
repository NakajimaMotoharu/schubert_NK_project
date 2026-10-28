"""Explicit public finally-context delta, not graph/native or whole static acceptance."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13768-main-finally-public-v1'
scan.BEFORE = '3368d2ac323c7806b2194f00f7a3816b83b1d45e'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/f03_main_finally_fifteen_trace.py')

if __name__ == '__main__':scan.main()
