"""Save pure closed projection plus preserved metadata-only correction and failed consumers."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17966-closed-projection-public-save-v1'
save.BEFORE='61e8258e6a32aecbc2c3d98fb0cc96ecfcfcb281'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1795','tools/quality/pg1796','tools/quality/architecture/ClosedProjectionValueContractTest.java','tools/quality/architecture/ClosedProjectionSixCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
