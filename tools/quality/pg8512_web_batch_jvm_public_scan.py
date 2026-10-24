"""Public Web/Batch standard JVM source/28 and exact role proof delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'b30fb832a6376d0e941ea6870fe8ad4ad7a31a53'
    scan.OUT = scan.scan.BASE / 'PG8512-web-batch-jvm-public-delta-v1'
    scan.main()

