"""Explicit public current Expiry whole4 evidence delta, not a global secret or native claim."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13736-expiry-observation-public-v1'
scan.BEFORE = 'bd313c6702f07d7852acee6b38abe1bd2a1c12b0'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg137','tools/quality/architecture/ExpiryObservationCurrentFourJunitLauncher.java')

if __name__ == '__main__':scan.main()
