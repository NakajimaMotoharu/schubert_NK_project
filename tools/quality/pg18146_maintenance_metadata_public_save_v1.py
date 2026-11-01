"""Save only qualified maintenance metadata evidence; held paths excluded before metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18146-maintenance-metadata-public-save-v1'
save.BEFORE='8a87c934ed36340b4004f29bd4cb856d3d8be3da'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1813','tools/quality/pg1814','tools/quality/architecture/MaintenanceMetadataContractTest.java','tools/quality/architecture/MaintenanceMetadataSixCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
