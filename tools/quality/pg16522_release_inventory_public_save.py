"""Exact public release JSON parser delta; held files excluded before content/metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16522-release-inventory-public-save-v1'
save.BEFORE='c36fcd5a11e7e872251363af252fdb3aeb421f4e'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16508_','tools/quality/pg16510_','tools/quality/pg16512_','tools/quality/pg16514_','tools/quality/pg16516_','tools/quality/pg16518_','tools/quality/pg16520_','tools/quality/pg16522_','tools/quality/architecture/ReleaseInventorySixteenCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
