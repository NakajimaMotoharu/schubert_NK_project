"""Preservation public metadata delta only; no data scanner, target or test actions."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='2427f90c2b45073b9ffb112f4f1554d1259dbdd6'
    scan.OUT=scan.scan.BASE/'PG9324-g13-storage-preservation-public-delta-v1'
    scan.main()
