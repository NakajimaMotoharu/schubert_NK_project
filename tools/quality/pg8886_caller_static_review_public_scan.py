"""Bounded public review delta only, not complete451 secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='c59c3ef60'
    scan.OUT=scan.scan.BASE/'PG8886-caller-static-review-public-delta-v1'
    scan.main()
