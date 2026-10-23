"""Bounded public delta/three known secret formats only; never private/runtime paths."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='940568b38'
    scan.OUT=scan.scan.BASE/'PG7544-async-byte-unit-public-delta-v1'
    scan.main()
