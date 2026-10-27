"""Explicit public metadata-tool delta scan only, no held content access."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12712-fixture-advisory-public-v1'
scan.BEFORE = '0bcd337960b46dd8c69928ba3246d79531931d51'
scan.PREFIXES = (*scan.PREFIXES, 'tools/quality/fixture_scope_advisory.py')

if __name__ == '__main__':
    scan.main()
