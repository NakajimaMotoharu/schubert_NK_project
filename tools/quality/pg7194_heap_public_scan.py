"""Known-three-format scan of current public delta only, no private/actual runtime access."""
import pg6990_recovery_public_scan as scan


if __name__=='__main__':
    scan.BEFORE='3343f93324a37244a654e92a43910d723bce0ab4'
    scan.OUT=scan.scan.BASE/'PG7194-heap-public-delta-v1'
    scan.main()
