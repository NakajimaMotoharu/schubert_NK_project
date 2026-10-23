"""Exact public group delta only; no runtime/private scan or sensitive values."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='333ffb46ef400bf903e4d4593f8e5e127f4a0f66'
    scan.OUT=scan.scan.BASE/'PG8048-exact-duration-public-delta-v5'
    scan.main()
