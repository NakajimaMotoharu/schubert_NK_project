"""Public policy-alert-status connection evidence delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE='fa5da98946dba3e55197ca9a30361230b74b9449'
    scan.OUT=scan.scan.BASE/'PG8664-policy-alert-status-public-delta-v1'
    scan.main()
