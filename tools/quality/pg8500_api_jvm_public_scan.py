"""Public API standard JVM source/14 and both preserved quality failures delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '91c3a1dc5416346d5637fba18130edac4a992e43'
    scan.OUT = scan.scan.BASE / 'PG8500-api-jvm-public-delta-v1'
    scan.main()

