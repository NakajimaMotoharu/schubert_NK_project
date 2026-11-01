"""Exact original denial4 and compile-closure repair, preserve failed run bytes."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17676-root-entry-denial-public-save-v1'
save.BEFORE = 'b6b14110213d7d741cf02a7b3bb5fad822c65590'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1766', 'tools/quality/pg1767', 'tools/quality/architecture/RootEntryDenialFourCurrentJunitLauncher.java', 'tools/quality/architecture/RootContextCtorOnlyProbeAuditV1.java')
if __name__ == '__main__':
    save.main()
