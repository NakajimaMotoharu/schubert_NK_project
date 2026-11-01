"""Save internal menu projection qualifications without copying Current or touching held inputs."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18126-menu-projection-public-save-v1'
save.BEFORE='87c10fde3440437524a9871976cde4d7d60b5670'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1811','tools/quality/pg1812','tools/quality/architecture/MenuProjectionContractTest.java','tools/quality/architecture/MenuProjectionSixCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
