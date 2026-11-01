"""Save technical metadata evidence only; retain held inputs unchanged."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18266-session-technical-public-save-v1'
save.BEFORE='9d62d676d329831e8dc389d7a31449f99fe600b7'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1825','tools/quality/pg1826','tools/quality/architecture/SessionTechnicalValueContractTest.java','tools/quality/architecture/SessionTechnicalEightCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
