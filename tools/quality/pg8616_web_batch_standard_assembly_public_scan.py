"""Public role-local standard three-phase composition PT and trace delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '63bba1575179770c13c709eec0e98981b0e2d04f'
    scan.OUT = scan.scan.BASE / 'PG8616-web-batch-standard-assembly-public-delta-v1'
    scan.main()
