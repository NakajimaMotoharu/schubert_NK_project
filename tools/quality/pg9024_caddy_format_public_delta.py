"""Caddy source/spec/result public delta only; three patterns, no whole secret-gate claim."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='512ecbed0cb68c4035e41e9c3cefb73a22e953d7'
    scan.OUT=scan.scan.BASE/'PG9024-caddy-format-public-delta-v1'
    scan.main()
