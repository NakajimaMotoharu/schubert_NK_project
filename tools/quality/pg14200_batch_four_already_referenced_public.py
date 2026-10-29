"""Publish duplicate-scope preflight as reauthentication, never new PG/PT completion."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14200-batch-four-already-referenced-public-v1'
scan.BEFORE = '0f1310e57fdcbfd6a2084652be676a27d00c3c15'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/pg142')

if __name__ == '__main__':scan.main()
