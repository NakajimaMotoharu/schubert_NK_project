"""Exact permit data6 and finite source-line guard repair, old failure retained."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17656-current-permit-data-public-save-v1'
save.BEFORE = 'b51e729b124be33c238e5233c9272e91ca950de2'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1764', 'tools/quality/pg1765', 'tools/quality/architecture/CurrentPermitDataSixCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
