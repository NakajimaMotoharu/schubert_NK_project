"""Exact public delta scan, held names removed before content access; no application execution."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13354-authority-oracle-public-v1'
scan.BEFORE = 'cb523fcc7538f8b16736e18a6aa803f6bb0879e0'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg133','tools/quality/f03_authority_oracle_sources.py','tools/quality/f03_authority_oracle_sources_v2.py')
if __name__ == '__main__':scan.main()
