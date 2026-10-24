"""Public tool-only installation metadata and syntax evidence; never binary/private files."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='c443a0e3c8beb6d2c3b23077fc5b4d42fb5e1457'
    scan.OUT=scan.scan.BASE/'PG8166-promtool-public-delta-v1'
    scan.main()
