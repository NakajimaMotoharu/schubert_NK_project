"""Exact schema-nine and consumption-review public delta; held names excluded first."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16742-schema-history-public-save-v1'
save.BEFORE='d984b23764f90366245ab68fcbdc4b82f0321bb5'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16728_','tools/quality/pg16730_','tools/quality/pg16732_','tools/quality/pg16734_','tools/quality/pg16736_','tools/quality/pg16738_','tools/quality/pg16740_','tools/quality/pg16742_','tools/quality/architecture/SchemaHistoryAdmissionNineCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
