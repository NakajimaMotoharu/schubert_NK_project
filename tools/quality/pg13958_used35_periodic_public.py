"""Explicit periodic technical/cost evidence; no inferred effort completion or dedicated cost."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13958-used35-periodic-public-v1'
scan.BEFORE = '31f59db2a07f85d30a28e9ba8d43d4aed813e542'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg139')

if __name__ == '__main__':scan.main()
