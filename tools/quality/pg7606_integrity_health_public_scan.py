"""Declared changed-public text scan/three known secret formats only, no private/runtime input."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='2ac589f2b'
    scan.OUT=scan.scan.BASE/'PG7606-integrity-health-public-delta-v1'
    scan.main()
