"""Exact public saved-static reference delta; exclude held files before metadata access."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17156-storage-pmd-identity-public-save-v1'
save.BEFORE = '353b106a275544a11a45fe37d0b82a5c6b7866e0'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17152_', 'tools/quality/pg17154_', 'tools/quality/pg17156_')
if __name__ == '__main__':
    save.main()
