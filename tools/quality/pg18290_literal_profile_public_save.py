"""Save small pure profile tool qualification only."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18290-literal-profile-public-save-v1'
save.BEFORE='77d06c1ca353d5604cdd49d28d5c9ef4b48307b8'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg18288','tools/quality/pg18289','tools/quality/pg18290','tools/quality/literal_profile_replace_v2.mjs')
if __name__=='__main__':save.main()
