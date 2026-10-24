"""Public fixed offline parser evidence delta, not a formal comprehensive secret gate."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '8ba0de63f3df9b0ec9ae0734ce990a22ed2821cd'
    scan.OUT = scan.scan.BASE / 'PG8656-prometheus-profile-parser-public-delta-v1'
    scan.main()
