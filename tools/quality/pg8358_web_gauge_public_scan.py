"""Public precision Web Gauge evidence/source delta only, no runtime/private scan."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'ca7771e172a99eb85e796339481b88a7d0f26aa4'
    scan.OUT = scan.scan.BASE / 'PG8358-web-gauge-public-delta-v1'
    scan.main()
