"""Explicit public changed text, excluding held names before metadata or content access."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16264-admission-reference-public-save-v1'
save.BEFORE='8e1c2699833245e8ffe200cff92e39041b749d74'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16260_',
    'tools/quality/pg16261_','tools/quality/pg16262_','tools/quality/pg16264_')

if __name__=='__main__':save.main()
