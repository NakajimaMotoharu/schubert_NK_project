"""Exact public batch phase Source-purpose delta; no native or permit operation."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16384-batch-phase-public-save-v1'
save.BEFORE='052e9708b3044efadb0bf19f5866f78662e4628d'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16380_',
    'tools/quality/pg16382_','tools/quality/pg16384_')

if __name__=='__main__':save.main()
