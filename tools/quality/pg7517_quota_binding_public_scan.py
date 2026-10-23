"""Necessary quota-binding public delta, without replaying Product or successful tool unit tests."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='255064aee'
    scan.OUT=scan.scan.BASE/'PG7517-quota-binding-public-delta-v1'
    scan.main()
