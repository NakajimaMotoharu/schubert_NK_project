"""Exact original Expiry owner two, failed metadata versions and finite remediation records."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17496-expiry-owner-public-save-v1'
save.BEFORE = 'c26b046f26b0513e5407bb560b831c1ba1424224'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17480_', 'tools/quality/pg17482_', 'tools/quality/pg17484_', 'tools/quality/pg17485_', 'tools/quality/pg17488_', 'tools/quality/pg17490_', 'tools/quality/pg17491_', 'tools/quality/pg17492_', 'tools/quality/pg17494_', 'tools/quality/pg17496_', 'tools/quality/architecture/ExpiryOwnerTwoCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
