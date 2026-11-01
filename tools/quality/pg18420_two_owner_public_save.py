"""Save two bounded owner corrections and explicitly open horizontal follow-ups."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18420-two-owner-public-save-v1'
save.BEFORE='e21b7d7c67be1b7226e0269e74a97923ebcc8c33'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1841','tools/quality/pg1842','tools/quality/trace_owner_explicit_query_v2.py')
if __name__=='__main__':save.main()
