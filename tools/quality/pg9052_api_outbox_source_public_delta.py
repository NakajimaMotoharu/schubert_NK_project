"""API service source and sanitized evidence delta only; not full G07."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='3ec4d9ca49fe694a9fe828e39d3cefcb1992b13f'
    scan.OUT=scan.scan.BASE/'PG9052-api-outbox-source-public-delta-v1'
    scan.main()
