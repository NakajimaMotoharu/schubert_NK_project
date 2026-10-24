"""Bounded public HTTP lifetime repair and evidence text only, never target/private data."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'd68cb47cd178a00dc0efd42528aa400d576c4330'
    scan.OUT = scan.scan.BASE / 'PG8306-http-cdf-public-delta-v1'
    scan.main()
