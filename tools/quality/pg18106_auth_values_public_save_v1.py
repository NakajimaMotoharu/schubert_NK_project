"""Save nine pure auth value/catalog Source qualifications without secret or held inputs."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18106-auth-values-public-save-v1'
save.BEFORE='a45bb4efa80fa824c368b6112b1dce458e927d4c'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1809','tools/quality/pg1810','tools/quality/architecture/AuthImmutableValueContractTest.java','tools/quality/architecture/AuthValuesTwelveCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
