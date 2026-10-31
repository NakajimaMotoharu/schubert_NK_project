"""Exact public JMS Source-purpose delta, held files excluded before metadata/content."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16348-jms-generic-public-save-v1'
save.BEFORE='de34ccc443d5a8cbdaaea98ea70063d667f6a11c'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16344_',
    'tools/quality/pg16345_','tools/quality/pg16346_','tools/quality/pg16348_')

if __name__=='__main__':save.main()
