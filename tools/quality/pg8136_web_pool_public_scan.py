"""Web pool public delta only; no runtime or private input."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='cc653abb2bca443d55c42e508fa738a095a75384'
    scan.OUT=scan.scan.BASE/'PG8136-web-pool-public-delta-v1'
    scan.main()
