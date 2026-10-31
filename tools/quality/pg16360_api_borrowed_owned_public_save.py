"""Exact public API Source-purpose evidence delta; excludes held names before metadata/content."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16360-api-borrowed-owned-public-save-v1'
save.BEFORE='a39da9787012a7f7be8859279c89f26d9ac49601'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16356_',
    'tools/quality/pg16358_','tools/quality/pg16360_')

if __name__=='__main__':save.main()
