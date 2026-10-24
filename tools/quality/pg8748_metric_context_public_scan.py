"""Public caller-held context same-source quality delta only."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='08eec31b9'
    scan.OUT=scan.scan.BASE/'PG8748-metric-context-public-delta-v1'
    scan.main()
