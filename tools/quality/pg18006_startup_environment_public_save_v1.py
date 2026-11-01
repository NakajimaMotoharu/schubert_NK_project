"""Save independent environment guards and original input proofs, not actual startup or keys."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18006-startup-environment-public-save-v1'
save.BEFORE='bd801e101ad6b52248d36229b400f8d76f2b18ab'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1799','tools/quality/pg1800','tools/quality/architecture/ApiEnvironmentGateContractTest.java','tools/quality/architecture/WebEnvironmentGateContractTest.java','tools/quality/architecture/StartupEnvironmentTenCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
