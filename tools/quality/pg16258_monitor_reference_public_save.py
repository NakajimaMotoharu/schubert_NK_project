"""Public text delta with held-file pre-exclusion, no whole quality acceptance claim."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16258-monitor-reference-public-save-v1'
save.BEFORE='6ca7e686d4e45bf66ca3af151fddd50658fd4091'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16254_',
    'tools/quality/pg16256_','tools/quality/pg16258_')

if __name__=='__main__':save.main()
