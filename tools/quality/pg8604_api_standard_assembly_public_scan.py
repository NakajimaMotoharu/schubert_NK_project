"""Public API standard composition and source-mutator tool repair delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'b161c86126cc767973d38bffcb69a7a52d212f63'
    scan.OUT = scan.scan.BASE / 'PG8604-api-standard-assembly-public-delta-v1'
    scan.main()
