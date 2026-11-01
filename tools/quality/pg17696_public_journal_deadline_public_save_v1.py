"""Exact original journal/deadline9 current-source qualification."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17696-public-journal-deadline-public-save-v1'
save.BEFORE = '553eccb277a9dce27fc4b0b5edb2234e4c410f5c'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1768', 'tools/quality/pg1769', 'tools/quality/architecture/PublicJournalDeadlineNineCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
