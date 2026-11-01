"""Save exact media-display evidence delta, excluding held inputs before metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18246-media-display-public-save-v1'
save.BEFORE='532c78423b319dae83a00c87c80508ef24a31ee0'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1823','tools/quality/pg1824','tools/quality/architecture/MediaDisplayContractTest.java','tools/quality/architecture/MediaDisplayTwelveCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
