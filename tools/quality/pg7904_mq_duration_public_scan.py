"""Bounded own public delta and three known secret formats, no runtime/private input."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='2c2ca695218ae473f5614e4e6afe0bfc36f5a95c'
    scan.OUT=scan.scan.BASE/'PG7904-mq-duration-public-delta-v1'
    scan.main()
