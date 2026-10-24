"""Current Web service metric public delta only, not full451 secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='63379722e'
    scan.OUT=scan.scan.BASE/'PG8942-web-service-metric-public-delta-v1'
    scan.main()
