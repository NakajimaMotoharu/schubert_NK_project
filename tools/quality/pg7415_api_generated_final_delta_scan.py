"""Necessary final changed-public delta after fresh quota checkpoint correction; not an old PT replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='39c0915c5'
    scan.OUT=scan.scan.BASE/'PG7415-api-generated-final-public-delta-v1'
    scan.main()
