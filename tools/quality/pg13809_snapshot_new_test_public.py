"""Explicit public new literal-value Test and pre-execution specification only."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13809-snapshot-new-test-public-v1'
scan.BEFORE = 'c5316a5d5091f0435c0a8007197070f52bdbed64'
scan.PREFIXES = (*scan.PREFIXES,'src/','tools/quality/pg13809_snapshot_new_test_public.py')

if __name__ == '__main__':scan.main()
