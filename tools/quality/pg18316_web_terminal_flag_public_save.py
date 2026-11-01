"""Save pure captured flag evidence and fixed-profile generation receipt."""
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18316-web-terminal-flag-public-save-v1'
save.BEFORE='5a1ccdfac0b05c0bcea9448a5d772c697b169a82'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg18299','tools/quality/pg1830','tools/quality/pg1831','tools/quality/architecture/WebTerminalFlagContractTest.java','tools/quality/architecture/WebTerminalFlagFourCurrentJunitLauncher.java')
if __name__=='__main__':save.main()
