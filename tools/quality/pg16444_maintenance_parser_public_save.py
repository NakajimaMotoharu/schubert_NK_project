"""Exact public maintenance parser/quality-vector delta, held names excluded before content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16444-maintenance-parser-public-save-v1'
save.BEFORE='e443a7f7bb790424c153ce9eef259b0e626a260d'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16430_','tools/quality/pg16432_','tools/quality/pg16434_','tools/quality/pg16436_','tools/quality/pg16438_','tools/quality/pg16440_','tools/quality/pg16442_','tools/quality/pg16444_','tools/quality/architecture/MaintenanceObservedValuesContractTest.java','tools/quality/architecture/MaintenanceSnapshotEightJunitLauncher.java')
if __name__=='__main__':save.main()
