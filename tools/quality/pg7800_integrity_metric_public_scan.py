"""Own public delta, three known secret formats only; no private/runtime inputs."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='da216fbd1'
    scan.OUT=scan.scan.BASE/'PG7800-integrity-metric-public-delta-v1'
    scan.main()
