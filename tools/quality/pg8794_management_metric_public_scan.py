"""Management metric PG/public scoped quality delta, not complete451 secret gate."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='ad3a6cead'
    scan.OUT=scan.scan.BASE/'PG8794-management-metric-public-delta-v1'
    scan.main()
