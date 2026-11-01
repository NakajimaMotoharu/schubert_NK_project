"""Save passive Caddy supplement; all held inputs excluded before metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18066-caddy-passive-public-save-v1'
save.BEFORE='32a08ad595bc8af99543dc6f3e68fea410f1d34b'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1805','tools/quality/pg1806')
if __name__=='__main__':save.main()
