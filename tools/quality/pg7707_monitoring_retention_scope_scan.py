"""Own public audit delta, known secret-format scan only, no private/runtime read."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='9df2352b5d25e06c6751c1814f901a097ccb7a4a'
    scan.OUT=scan.scan.BASE/'PG7707-monitoring-retention-scope-public-delta-v1'
    scan.main()
