"""Finite changed-public scan, held files removed before content access."""
import pg12706_scenario_writer_public as scan
scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13284-business-boundary-public-v1'
scan.BEFORE = '4a174d43ff4416665eb118d39beed83bfe1e0b99'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg132')
if __name__ == '__main__':scan.main()
