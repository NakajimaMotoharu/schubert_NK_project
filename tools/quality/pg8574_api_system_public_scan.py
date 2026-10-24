"""Public API standard CPU-FD selected PT and qualification delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'b59c4857ddeaf19fe9dc684375aedeca1c99e948'
    scan.OUT = scan.scan.BASE / 'PG8574-api-system-public-delta-v1'
    scan.main()
