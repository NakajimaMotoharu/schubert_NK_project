"""Public four-exporter identity repair and failed/successful evidence delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '4234e0ffdb5f5171fb087784cf68b6c6ab9e4630'
    scan.OUT = scan.scan.BASE / 'PG8390-metric-identity-public-delta-v1'
    scan.main()
