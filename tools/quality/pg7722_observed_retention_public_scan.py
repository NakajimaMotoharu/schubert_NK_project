"""Own changed public text, three known secret formats only, no private/runtime reads."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='4e56c6ca8'
    scan.OUT=scan.scan.BASE/'PG7722-observed-retention-public-delta-v1'
    scan.main()
