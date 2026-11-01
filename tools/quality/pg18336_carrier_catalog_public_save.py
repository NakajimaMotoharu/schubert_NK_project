"""Save immutable carrier failures, corrected tests and qualified evidence."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18336-carrier-catalog-public-save-v1'
save.BEFORE='49fe76541d3af1397b04f52f9542c3f58c390baa'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1831','tools/quality/pg1832','tools/quality/pg1833','tools/quality/architecture/CarrierCatalogFiveCurrentJunitLauncher.java','tools/quality/architecture/CarrierCatalogFiveV2CurrentJunitLauncher.java','tools/quality/architecture/CompositeMvcBeanDeclarationContractTestV2.java','tools/quality/architecture/CompositeMvcDeclarationContractTest.java','tools/quality/architecture/CoverageDeclaredMethodWitnessV1.java','tools/quality/architecture/InboxFailureValueContractTest.java','tools/quality/architecture/ProjectionFailureValueContractTest.java','tools/quality/architecture/ScenarioCarrierSuccessContractTest.java')
if __name__=='__main__':save.main()
