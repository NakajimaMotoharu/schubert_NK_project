"""Exact Bootstrap callback-closing public delta; held files excluded before access."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16774-bootstrap-closing-public-save-v1'
save.BEFORE='74bbe6871351e8d88e85c6d65883d300f4d7ac31'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16760_','tools/quality/pg16762_','tools/quality/pg16764_','tools/quality/pg16766_','tools/quality/pg16768_','tools/quality/pg16770_','tools/quality/pg16772_','tools/quality/pg16774_','tools/quality/architecture/BootstrapClosingThreeCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
