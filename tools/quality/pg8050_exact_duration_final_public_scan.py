"""Final group public text delta including earlier scan, never private/runtime artifacts."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='333ffb46ef400bf903e4d4593f8e5e127f4a0f66'
    scan.OUT=scan.scan.BASE/'PG8050-exact-duration-final-public-delta-v5'
    scan.main()
