"""Exact public question/local audit review delta; no Product or Graph action."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16396-question-local-audit-public-save-v1'
save.BEFORE='4090ac170f055f61238fef70f283c6cd422f6b60'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16392_',
    'tools/quality/pg16394_','tools/quality/pg16396_')

if __name__=='__main__':save.main()
