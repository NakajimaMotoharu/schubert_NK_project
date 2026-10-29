"""Explicit public eight value-frame tests and independent complete-unit result."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13858-startup-proof-public-v1'
scan.BEFORE = '30b4a00768aa00481c877424c47cddbbdb9b8605'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg138','tools/quality/architecture/StartupProofFrameCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
