"""Only current changed public metadata/known three formats; no private logs/runtime or all-secret claim."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='ae36388db'
    scan.OUT=scan.scan.BASE/'PG7419-generated-inventory-public-delta-v1'
    scan.main()
