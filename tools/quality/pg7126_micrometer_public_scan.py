"""Bounded current public delta scan, no private/runtime data and no claim of all-secret absence."""
import pg6990_recovery_public_scan as scan


if __name__=='__main__':
    scan.BEFORE='3343f93324a37244a654e92a43910d723bce0ab4'
    scan.OUT=scan.scan.BASE/'PG7126-micrometer-public-delta-v1'
    scan.main()
