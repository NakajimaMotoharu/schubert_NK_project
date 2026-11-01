"""Save latest-primary270 owner metadata correction without runtime or acceptance transfer."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18464-latest270-owner-public-save-v1'
save.BEFORE='4746c687515d0c268e86e69d130c0ce1294156d6'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1845','tools/quality/pg1846','tools/quality/trace_owner_latest_primary_v4.py')
if __name__=='__main__':save.main()
