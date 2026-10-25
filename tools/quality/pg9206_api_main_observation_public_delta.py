"""Public Main wiring delta; not full G07 or runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='4b064b00e73ff2f7d907289ce0e79895d57e3063'
    scan.OUT=scan.scan.BASE/'PG9206-api-main-observation-public-delta-v1'
    scan.main()
