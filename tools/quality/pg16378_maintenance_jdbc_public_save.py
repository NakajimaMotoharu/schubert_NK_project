"""Exact public maintenance catch-purpose delta; no actual maintenance operation."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16378-maintenance-jdbc-public-save-v1'
save.BEFORE='cd881ded23582b363f189a52ee3d95cb124a981c'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16374_',
    'tools/quality/pg16376_','tools/quality/pg16378_')

if __name__=='__main__':save.main()
