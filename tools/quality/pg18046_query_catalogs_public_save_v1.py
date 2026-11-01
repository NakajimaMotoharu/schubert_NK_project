"""Save the five fixed query catalog qualification without touching held inputs."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18046-query-catalogs-public-save-v1'
save.BEFORE='bfdd9e3f8d42133302023c72d6c3da60df43f3f7'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1803','tools/quality/pg1804','tools/quality/architecture/QueryCatalogContractTest.java','tools/quality/architecture/QueryCatalogFiveCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
