"""Bounded public summary-encoder source/PT/tool/evidence delta, no private inputs."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '470034db210d2f3008ac65c64e4c36037d586fba'
    scan.OUT = scan.scan.BASE / 'PG8280-summary-encoder-public-delta-v1'
    scan.main()
