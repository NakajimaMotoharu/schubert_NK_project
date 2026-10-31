"""Public text delta save with exact held-name exclusion, no whole-G07 acceptance claim."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16252-legacy-fourteen-public-save-v1'
save.BEFORE='c1a4c949453a278f0bd7cd7e84aa80628e3b7875'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16248_',
    'tools/quality/pg16250_','tools/quality/pg16252_')

if __name__=='__main__':save.main()
