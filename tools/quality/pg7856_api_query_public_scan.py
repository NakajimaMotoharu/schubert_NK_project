"""Own public delta only and three known secret formats, not runtime or private logs."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='060738047987b46d2818da0639e49a3eee47f57c'
    scan.OUT=scan.scan.BASE/'PG7856-api-query-public-delta-v1'
    scan.main()
