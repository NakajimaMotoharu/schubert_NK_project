"""Bounded own public audit delta, three known secret formats only, no actual runtime inputs."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='9c1b72cb01d93bcc550bd34e169a4a1464f0ecec'
    scan.OUT=scan.scan.BASE/'PG7934-monitoring-scope-public-delta-v1'
    scan.main()
