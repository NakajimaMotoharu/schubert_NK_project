"""Public token provenance delta only; not a whole secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='1f69fa62e65560e65a84d7b0b7032b04b82aef28'
    scan.OUT=scan.scan.BASE/'PG9006-g07-token-public-delta-v1'
    scan.main()
