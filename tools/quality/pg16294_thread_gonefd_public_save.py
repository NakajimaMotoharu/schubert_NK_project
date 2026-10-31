"""Exact public Source-purpose delta only, no held metadata/content or global G07 assertion."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16294-thread-gonefd-public-save-v1'
save.BEFORE='d6dc2e3acd5840814a99368f42239ec9b09a81ff'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16290_',
    'tools/quality/pg16291_','tools/quality/pg16292_','tools/quality/pg16294_')

if __name__=='__main__':save.main()
