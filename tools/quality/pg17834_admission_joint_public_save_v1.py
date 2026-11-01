"""Save independent admission wait quality PT and one-source four-counter proof."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17834-admission-joint-public-save-v1'
save.BEFORE='38cfc28168a1e07d10a6b08149f8c12a67ca8782'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1781','tools/quality/pg1782','tools/quality/pg1783','tools/quality/scoped_prometheus_owned_admission_wait_host_v1.py','tools/quality/owned_admission_wait_environment_step_v1.py','tools/quality/architecture/AdmissionActualWaitFiveCurrentJunitLauncher.java','tools/quality/architecture/WebHttpAdmissionWaitingContractTest.java')
if __name__=='__main__':save.main()
