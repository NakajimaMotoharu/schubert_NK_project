"""Save User display proofs and exact before/after oracle basis, without touching held inputs."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18226-user-display-public-save-v1'
save.BEFORE='a9df619924feded41687afed9110922830242939'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1821','tools/quality/pg1822','tools/quality/architecture/UserDisplayContractTest.java','tools/quality/architecture/UserDisplayEightCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
