"""Public API approved mode/source/94 and preserved static stop delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'f433ebcfe2de79737a1e84d7e4f175087e3363a8'
    scan.OUT = scan.scan.BASE / 'PG8446-api-approved-policy-public-delta-v1'
    scan.main()

