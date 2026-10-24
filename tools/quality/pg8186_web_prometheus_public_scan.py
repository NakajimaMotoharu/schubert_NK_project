"""Declared public SDK gauge/counter PT delta only, never private or target data."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='95b0ab345f73568f48a791ef5036ab34abd653a0'
    scan.OUT=scan.scan.BASE/'PG8186-web-prometheus-public-delta-v1'
    scan.main()
