"""Bounded G13 metadata delta only, not a whole repository secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='61ad54609db71cceb737ebe884c9d6f032f47182'
    scan.OUT=scan.scan.BASE/'PG9308-g13-registered-owner-public-delta-v1'
    scan.main()
