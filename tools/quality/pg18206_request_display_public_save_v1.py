"""Save bundled request-only display qualification and five-pp audit, excluding held files."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18206-request-display-public-save-v1'
save.BEFORE='4fb6484ae6366d4e714bd9295d60475de6d7bc26'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1819','tools/quality/pg1820','tools/quality/architecture/RequestDisplayContractTest.java','tools/quality/architecture/RequestDisplayTenCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
