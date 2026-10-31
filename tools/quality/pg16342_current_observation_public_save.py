"""Exact public synthetic-wrapper delta; held files excluded before metadata or content."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16342-current-observation-public-save-v1'
save.BEFORE='2524b73981fc9425431310ade312a999502cabff'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16328_',
    'tools/quality/pg16330_','tools/quality/pg16332_','tools/quality/pg16334_',
    'tools/quality/pg16336_','tools/quality/pg16338_','tools/quality/pg16340_',
    'tools/quality/pg16342_','tools/quality/architecture/CurrentObservationOneJunitLauncher.java')

if __name__=='__main__':save.main()
