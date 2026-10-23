"""Declared changed-public text/three known secret formats only, no private/runtime input."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='c4c75f000'
    scan.OUT=scan.scan.BASE/'PG7590-restart-health-public-delta-v1'
    scan.main()
