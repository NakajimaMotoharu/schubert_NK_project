"""Exact encoder3 public delta; exclude held paths before content or metadata."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16570-management-encoder-public-save-v1'
save.BEFORE='4386420e15c1385759c89ba1b60a11499f502fba'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16556_','tools/quality/pg16558_','tools/quality/pg16560_','tools/quality/pg16562_','tools/quality/pg16564_','tools/quality/pg16566_','tools/quality/pg16568_','tools/quality/pg16570_','tools/quality/architecture/ManagementEncoderThreeCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
