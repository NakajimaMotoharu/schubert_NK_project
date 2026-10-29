"""Public36 pure state contract and complete Source technical evidence only."""
import pg12706_scenario_writer_public as scan

scan.OUT = scan.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14138-alert-state-whole-thirty-six-public-v1'
scan.BEFORE = '25bbf6b32e6e1798a04026ae2ce22f680d9f425b'
scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg141','tools/quality/architecture/AlertStateCurrentJunitLauncher.java')

if __name__ == '__main__':scan.main()
