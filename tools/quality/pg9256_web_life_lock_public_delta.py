"""Public Web owner remedy delta, not whole G07 or runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='087b157ac2cd7b042355988b52a5dd87f9bd44d7'
    scan.OUT=scan.scan.BASE/'PG9256-web-life-lock-public-delta-v1'
    scan.main()
