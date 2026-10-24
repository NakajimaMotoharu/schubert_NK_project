"""Public new same-source ready/standard/duration pipeline4 proof delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '284d731c59767b2a8f8696b7c566461e0d1ba398'
    scan.OUT = scan.scan.BASE / 'PG8648-metric-payload-precision-public-delta-v1'
    scan.main()
