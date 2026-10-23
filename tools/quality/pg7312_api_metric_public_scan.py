"""Final public known-three-format delta only, no actual DB/VM/private logs or all-secret claim."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='3343f93324a37244a654e92a43910d723bce0ab4'
    scan.OUT=scan.scan.BASE/'PG7312-api-metric-public-delta-v1'
    scan.main()
