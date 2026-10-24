"""Bounded catalog-role audit public text delta only; no runtime/private data."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='bc2588f66f4c7ca56194faa4a84764b47bb6b600'
    scan.OUT=scan.scan.BASE/'PG8118-catalog-role-public-delta-v1'
    scan.main()
