"""Finite changed-public-file scan, subtract held files before any content access."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13338-state-oracle-public-v1'
scan.BEFORE = 'c289427e0fc9f2c9b4b5f18683ee5733c9d41342'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg133','tools/quality/f03_state_oracle_sources.py')
if __name__ == '__main__':scan.main()
