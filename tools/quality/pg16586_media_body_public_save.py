"""Exact streamer2 public delta; exclude held paths before content/metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16586-media-body-public-save-v1'
save.BEFORE='8a44a792f6f526b94a98c6bb82caf8d8a9661d4c'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16572_','tools/quality/pg16574_','tools/quality/pg16576_','tools/quality/pg16578_','tools/quality/pg16580_','tools/quality/pg16582_','tools/quality/pg16584_','tools/quality/pg16586_','tools/quality/architecture/MediaBodyTwoCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
