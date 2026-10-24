"""Current Web metric caller public delta only, not full451 secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='4ae191923'
    scan.OUT=scan.scan.BASE/'PG8876-web-caller-metric-public-delta-v1'
    scan.main()
