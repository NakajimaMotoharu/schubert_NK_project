"""Declared changed-public text/three known secret formats only, no private/runtime paths."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='78092ab26'
    scan.OUT=scan.scan.BASE/'PG7622-dlq-health-public-delta-v1'
    scan.main()
