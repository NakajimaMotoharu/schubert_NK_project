"""Exact family-eight metadata delta; exclude held paths before metadata/content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16646-family-disclosure-public-save-v1'
save.BEFORE='2e4fbbc6607a09925f8e0e9c58b01e0104175f64'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16634_','tools/quality/pg16636_','tools/quality/pg16638_','tools/quality/pg16640_','tools/quality/pg16642_','tools/quality/pg16644_','tools/quality/pg16646_')
if __name__=='__main__':save.main()
