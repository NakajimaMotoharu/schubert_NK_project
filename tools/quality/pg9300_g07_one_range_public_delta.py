"""Public metadata diagnosis delta only; not a whole G07 scan."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='c4fd735b89718b33a24cd49addd754d879789927'
    scan.OUT=scan.scan.BASE/'PG9300-g07-one-range-public-delta-v1'
    scan.main()
