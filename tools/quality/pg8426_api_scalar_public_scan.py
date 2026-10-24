"""Public API scalar source/own32/qualification delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '6cd501efee479e5c52f5ef5ab8efe5d67e2552cd'
    scan.OUT = scan.scan.BASE / 'PG8426-api-scalar-public-delta-v1'
    scan.main()

