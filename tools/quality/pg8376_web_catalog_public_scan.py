"""Public closed-Web catalog/source and failed/successful quality evidence delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '2d88ac03cb06fcebf9adec732088b8f75f23956a'
    scan.OUT = scan.scan.BASE / 'PG8376-web-catalog-public-delta-v1'
    scan.main()
