"""Current API metric caller public delta only, not full451 secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='3029f628fec7fe84669a7dd6e3132d2567f21cf0'
    scan.OUT=scan.scan.BASE/'PG8864-api-caller-metric-public-delta-v1'
    scan.main()
