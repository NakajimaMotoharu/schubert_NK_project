"""Save pure ready plus necessary healthy repeat, without held sources or actual services."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17946-web-ready-public-save-v1'
save.BEFORE='d4c696e219300b763e543a59d9324b227a47ca97'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1793','tools/quality/pg1794','tools/quality/architecture/WebReadyPresenceContractTest.java','tools/quality/architecture/WebReadyPureSixCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
