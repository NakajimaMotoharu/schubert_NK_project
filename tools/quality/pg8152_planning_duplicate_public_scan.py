"""Public selection correction and guard evidence only; no operational input."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='e5dbaba83078e717580b1719b6c1c9f6f3f32591'
    scan.OUT=scan.scan.BASE/'PG8152-planning-duplicate-public-delta-v1'
    scan.main()
