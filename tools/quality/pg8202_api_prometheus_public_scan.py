"""Declared public API SDK fixture/post delta only, no target/private data."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='4daa32d72ef5586100d692da61681761ac7e1a14'
    scan.OUT=scan.scan.BASE/'PG8202-api-prometheus-public-delta-v1'
    scan.main()
