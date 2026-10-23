"""Own public delta only; three known secret formats, no private/runtime inputs."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='f7509aaa1'
    scan.OUT=scan.scan.BASE/'PG7826-restart-metric-public-delta-v1'
    scan.main()
