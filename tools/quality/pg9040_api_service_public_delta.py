"""API service source and sanitized evidence delta only; not full G07."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='b628e82a26c0652fbcbb24d82f925dee75f08c2b'
    scan.OUT=scan.scan.BASE/'PG9040-api-service-public-delta-v1'
    scan.main()
