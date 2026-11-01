"""Exact C08 twelve-obligation read-only audit save, no acceptance or Product mutation."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17564-c08-contract-public-save-v1'
save.BEFORE = '8a81aa19570461a6e9ce412a9e867fbda5db208d'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17560_', 'tools/quality/pg17562_', 'tools/quality/pg17564_')
if __name__ == '__main__':
    save.main()
