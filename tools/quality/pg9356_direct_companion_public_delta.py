"""Public static-tool/trace delta only; not a whole secret or production quality gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='55e8eb10e637380496e96acb2329f25ecabd02b0'
    scan.OUT=scan.scan.BASE/'PG9356-direct-companion-public-delta-v1'
    scan.main()
