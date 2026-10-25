"""Preserve the unqualified initial producer and independent metadata counterexample."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='854c8b6e2cee973939fdffa05cca9121d6f9450c'
    scan.OUT=scan.scan.BASE/'PG9601-explicit-case-failure-public-delta-v1'
    scan.main()
