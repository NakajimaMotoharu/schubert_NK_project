"""Public pure legacy-ready/custom payload PG/PT and immutable endpoint byte delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '65c3caadb3a9083309b0882cedad14ee9224f92e'
    scan.OUT = scan.scan.BASE / 'PG8640-api-web-custom-payload-public-delta-v1'
    scan.main()
