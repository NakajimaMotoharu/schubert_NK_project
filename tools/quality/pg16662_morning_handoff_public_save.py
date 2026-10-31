"""Exact handoff-eight public delta; held names excluded before content and metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16662-morning-handoff-public-save-v1'
save.BEFORE='838d6bddcc597ad5a215324b0ad0baf6af30b3f3'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16648_','tools/quality/pg16650_','tools/quality/pg16652_','tools/quality/pg16654_','tools/quality/pg16656_','tools/quality/pg16658_','tools/quality/pg16660_','tools/quality/pg16662_')
if __name__=='__main__':save.main()
