"""New public delta snapshot after precommit documentation line-count correction; no test replay."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16275-measurement-leaf-public-save-v2'
save.BEFORE='845349027e4f63cdb142ce6f5a432e63a162c79c'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16272_',
    'tools/quality/pg16273_','tools/quality/pg16275_')

if __name__=='__main__':save.main()
