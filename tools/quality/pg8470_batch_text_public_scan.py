"""Public Batch closed six-family text/source/32 and parser proof delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '5a2d73fb9ee51de826aab8d3bbf4f4ea4182b877'
    scan.OUT = scan.scan.BASE / 'PG8470-batch-text-public-delta-v1'
    scan.main()

