"""Exact public request trace10 delta; held files excluded before content/metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16506-web-trace-public-save-v1'
save.BEFORE='ccbae46ec5997e7d980e562b888572f5d7f2665b'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16492_','tools/quality/pg16494_','tools/quality/pg16496_','tools/quality/pg16498_','tools/quality/pg16500_','tools/quality/pg16501_','tools/quality/pg16502_','tools/quality/pg16504_','tools/quality/pg16506_','tools/quality/architecture/WebRequestTraceTenCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
