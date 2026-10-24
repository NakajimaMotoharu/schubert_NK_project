"""Public Web Counter/source fixture and tool lint correction evidence delta, not runtime scan."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'a3bfa44a3928e3f24b04871f5bf64cf01f0be035'
    scan.OUT = scan.scan.BASE / 'PG8346-web-counter-public-delta-v1'
    scan.main()
