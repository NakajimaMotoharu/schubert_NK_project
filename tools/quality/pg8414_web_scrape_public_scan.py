"""Public pure mode policy/source and metadata field-parser correction delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'cd43c1adb1a48eeb33e777a0b62228427413ce7e'
    scan.OUT = scan.scan.BASE / 'PG8414-web-scrape-public-delta-v1'
    scan.main()
