"""Exact original proxy3 public evidence without any live broker action."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17214-artemis-startup-proxy-public-save-v1'
save.BEFORE = 'ddb808287215480cede9ccd264106b17d31bd39b'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg17200_', 'tools/quality/pg17202_', 'tools/quality/pg17204_', 'tools/quality/pg17206_', 'tools/quality/pg17208_', 'tools/quality/pg17210_', 'tools/quality/pg17212_', 'tools/quality/pg17214_', 'tools/quality/architecture/ArtemisStartupProxyThreeCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
