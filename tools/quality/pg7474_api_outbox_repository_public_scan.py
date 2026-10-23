"""Changed public source/tools/results delta only, no real operation or original PT replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='4a29d9d89'
    scan.OUT=scan.scan.BASE/'PG7474-api-outbox-repository-public-delta-v1'
    scan.main()
