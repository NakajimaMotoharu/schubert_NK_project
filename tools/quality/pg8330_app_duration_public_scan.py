"""Public app duration/role correction evidence only; no runtime/private scan or global claim."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '4e7e2197eb8852b5172b652506dc2d1bb91f8681'
    scan.OUT = scan.scan.BASE / 'PG8330-app-duration-public-delta-v1'
    scan.main()
