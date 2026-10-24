"""Public new API owner PG/PT evidence delta only; not whole451 secret-gate acceptance."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='29313cb31'
    scan.OUT=scan.scan.BASE/'PG8698-api-standard-source-public-delta-v1'
    scan.main()
