"""Exact original auth borrowed fault3, public fixture effects and all partial denominators."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17756-auth-borrowed-boundary-public-save-v1'
save.BEFORE = 'ace2096b2c2012606d51e0e1e7fda0326eca1965'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1774', 'tools/quality/pg1775', 'tools/quality/architecture/AuthBorrowedBoundaryThreeCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
