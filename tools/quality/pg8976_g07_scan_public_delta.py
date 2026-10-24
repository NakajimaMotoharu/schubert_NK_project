"""G07 scan tool/evidence public delta; three format patterns, not whole secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='05d73a7974da8df92228160b96d91e7a006768f3'
    scan.OUT=scan.scan.BASE/'PG8976-g07-scan-public-delta-v1'
    scan.main()
