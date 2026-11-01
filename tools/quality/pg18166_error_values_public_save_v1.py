"""Save qualified pure error value evidence with failed tool history; held files excluded."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18166-error-values-public-save-v1'
save.BEFORE='647122176ad61704386a6ec2170d8aecd296cba2'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1815','tools/quality/pg1816','tools/quality/architecture/ErrorValueContractTest.java','tools/quality/architecture/ErrorValueSixCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
