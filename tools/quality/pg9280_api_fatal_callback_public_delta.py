"""Public same-source callback qualification only, not full G07/runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='e1b19e0e651ad840d5a4b24a70004fd2458f8156'
    scan.OUT=scan.scan.BASE/'PG9280-api-fatal-callback-public-delta-v1'
    scan.main()
