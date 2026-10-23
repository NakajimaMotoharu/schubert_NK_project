"""Necessary public changed-source/tool/evidence scan only, no actual/private input or PT replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='b49d3a048'
    scan.OUT=scan.scan.BASE/'PG7516-async-queue-public-delta-v1'
    scan.main()
