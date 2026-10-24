"""Public new SS26 role-schema cross-join6 and independent post delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'c07dc55c7621202a391b043683e5072a7cf6397b'
    scan.OUT = scan.scan.BASE / 'PG8520-metric-role-join-public-delta-v1'
    scan.main()

