"""Exact public POM original4 evidence; preserve held files and all original runs."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17244-runtime-pom-public-save-v1'
save.BEFORE = '550f66e3f0857182c3cc853d21819e30fdcb0afa'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17232_', 'tools/quality/pg17234_', 'tools/quality/pg17236_', 'tools/quality/pg17238_', 'tools/quality/pg17240_', 'tools/quality/pg17242_', 'tools/quality/pg17244_', 'tools/quality/architecture/RuntimePomFourCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
