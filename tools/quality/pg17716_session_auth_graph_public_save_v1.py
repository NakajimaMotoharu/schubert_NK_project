"""Exact graph8 four-counter qualification and disclosure repair without Product replay."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17716-session-auth-graph-public-save-v1'
save.BEFORE = '52fc424c686800e0a60397755bcfe81250a9b239'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1770', 'tools/quality/pg1771', 'tools/quality/architecture/SessionAuthGraphEightCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
