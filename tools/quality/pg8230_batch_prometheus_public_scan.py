"""Public Batch SDK and shared exact-scope audit delta; never target or private data."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='ec28bae997ba98407b415a9aedae507f466b90cd'
    scan.OUT=scan.scan.BASE/'PG8230-batch-prometheus-public-delta-v1'
    scan.main()
