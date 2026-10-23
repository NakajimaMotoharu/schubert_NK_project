"""Bounded changed-public text scan, three known secret formats only; no private/runtime reads."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='ddf57d298'
    scan.OUT=scan.scan.BASE/'PG7574-backup-health-public-delta-v1'
    scan.main()
