"""Exact original graph3, complete closure, natural B0 and metadata identity repair."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17736-revocation-graph-public-save-v1'
save.BEFORE = '74566fc7bf0b1965bac96c997d6e3eb9312537ee'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1772', 'tools/quality/pg1773', 'tools/quality/architecture/RevocationGraphThreeCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
