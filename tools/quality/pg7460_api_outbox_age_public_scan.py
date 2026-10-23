"""Necessary current changed-public delta, no private/runtime inputs or original test replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='0006ec651'
    scan.OUT=scan.scan.BASE/'PG7460-api-outbox-age-public-delta-v1'
    scan.main()
