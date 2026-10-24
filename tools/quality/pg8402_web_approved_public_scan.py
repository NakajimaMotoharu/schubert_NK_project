"""Public approved Web model join/source and bounded qualification evidence delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'bf7ceeed00ab2ef24250cb8317d8949ffe8dec46'
    scan.OUT = scan.scan.BASE / 'PG8402-web-approved-public-delta-v1'
    scan.main()
