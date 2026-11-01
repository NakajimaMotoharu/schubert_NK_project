"""Save same-byte24 owner correction and full horizontal non-applicable reasons."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18444-owner24-public-save-v1'
save.BEFORE='2db407b3f5d7c0fe6e1074b69a9387e2ed014073'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1843','tools/quality/pg1844','tools/quality/trace_owner_explicit_registry_v3.py')
if __name__=='__main__':save.main()
