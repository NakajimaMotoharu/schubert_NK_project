"""Own public text delta and three known secret formats only; no private/runtime inputs."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='3ebf839d1'
    scan.OUT=scan.scan.BASE/'PG7702-mq-pressure-connection-public-delta-v1'
    scan.main()
