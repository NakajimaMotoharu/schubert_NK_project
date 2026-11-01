"""Exact public-provider twelve and full partial Source8; no real native transfer."""
import pg12706_scenario_writer_public as save
save.OUT = save.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17636-checkpoint-public-provider-public-save-v1'
save.BEFORE = '07a156ef10851c3d1bd350fffca303dc1ef2fcba'
save.PREFIXES = ('documents/', 'evidence/01_PT/', 'tools/quality/pg1762', 'tools/quality/pg1763', 'tools/quality/architecture/CheckpointPublicProviderTwelveCurrentJunitLauncher.java')
if __name__ == '__main__':
    save.main()
