"""Public Batch closed label policy/source and exact14 qualification delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '68036a100'
    scan.OUT = scan.scan.BASE / 'PG8458-batch-label-policy-public-delta-v1'
    scan.main()

