"""Exact original Root ELF eight, partial Source and tool failures retained."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17326-root-elf-digest-public-save-v1'
save.BEFORE = '1faa9a78585efd181feb9822829d66ee5852c29d'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17310_', 'tools/quality/pg17312_', 'tools/quality/pg17314_', 'tools/quality/pg17318_', 'tools/quality/pg17320_', 'tools/quality/pg17321_', 'tools/quality/pg17322_', 'tools/quality/pg17323_', 'tools/quality/pg17324_', 'tools/quality/pg17326_', 'tools/quality/architecture/RootElfDigestEightCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
