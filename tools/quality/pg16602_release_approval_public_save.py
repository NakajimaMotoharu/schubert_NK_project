"""Exact public Approval8 delta; exclude held paths before content/metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16602-release-approval-public-save-v1'
save.BEFORE='349185cc9b169c87f1a004c1862d906d40d8eafa'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16588_','tools/quality/pg16590_','tools/quality/pg16592_','tools/quality/pg16594_','tools/quality/pg16596_','tools/quality/pg16598_','tools/quality/pg16600_','tools/quality/pg16602_','tools/quality/architecture/ApprovalEightCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
