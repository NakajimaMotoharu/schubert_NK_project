"""Current Batch full public delta including failures, not full451 secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='4ff357f72'
    scan.OUT=scan.scan.BASE/'PG8918-batch-full-text-public-delta-v1'
    scan.main()
