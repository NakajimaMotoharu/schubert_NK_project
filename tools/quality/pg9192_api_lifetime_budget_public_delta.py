"""Public Life/source/selected PT/partial quality delta only, not full G07 or runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='abc13b4d1409b07b202da3d986b1cd98680b185e'
    scan.OUT=scan.scan.BASE/'PG9192-api-lifetime-budget-public-delta-v1'
    scan.main()
