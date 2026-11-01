"""Save code-free population correction and preserved analyzer/profile failures."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG17866-codefree-public-save-v1'
save.BEFORE='4d946052bd4421f1134fe479595e5bab013404de'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1784','tools/quality/pg1785','tools/quality/pg1786')
if __name__=='__main__':save.main()
