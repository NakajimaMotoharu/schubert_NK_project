"""Public new same-registry actual coexist6 and independent metadata proof delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '095c133bd51e4e2de8bcc5c37f2aadec4f90cda7'
    scan.OUT = scan.scan.BASE / 'PG8624-metric-coexist-public-delta-v1'
    scan.main()
