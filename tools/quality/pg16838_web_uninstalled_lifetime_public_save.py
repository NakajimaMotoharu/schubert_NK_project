"""Exact uninstalled Web lifetime public4 delta; exclude held files before metadata/content."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG16838-web-uninstalled-lifetime-public-save-v1'
save.BEFORE='6145ed5ef7cf0abe6632abfce41aa9dfc2aa4c21'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg16824_','tools/quality/pg16826_','tools/quality/pg16828_','tools/quality/pg16830_','tools/quality/pg16832_','tools/quality/pg16834_','tools/quality/pg16836_','tools/quality/pg16838_','tools/quality/architecture/WebUninstalledLifetimeFourCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
