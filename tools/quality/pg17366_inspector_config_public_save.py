"""Exact original configuration four and whole Source four-counter qualification."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17366-inspector-config-public-save-v1'
save.BEFORE = '8ab1ec89aa7fdfb3d7456aeecc6652b31d48fbb2'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17350_', 'tools/quality/pg17352_', 'tools/quality/pg17354_', 'tools/quality/pg17358_', 'tools/quality/pg17360_', 'tools/quality/pg17362_', 'tools/quality/pg17364_', 'tools/quality/pg17366_', 'tools/quality/architecture/InspectorConfigFourCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
