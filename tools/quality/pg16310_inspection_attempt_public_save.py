"""Exact public pure-inspection delta; held files excluded before metadata/content."""
import pg12706_scenario_writer_public as save

save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16310-inspection-attempt-public-save-v1'
save.BEFORE='3ea2d03e7133d752b925e458195e3c12cf80a22a'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16296_',
    'tools/quality/pg16298_','tools/quality/pg16300_','tools/quality/pg16302_',
    'tools/quality/pg16304_','tools/quality/pg16306_','tools/quality/pg16308_',
    'tools/quality/pg16310_','tools/quality/architecture/InspectionAttemptEightJunitLauncher.java')

if __name__=='__main__':save.main()
