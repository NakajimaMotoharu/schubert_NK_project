"""Public role-local standard CPU-FD PT and trace delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'd07057e8672032415af256cc595c9c5e407121fb'
    scan.OUT = scan.scan.BASE / 'PG8586-web-batch-system-public-delta-v1'
    scan.main()
