"""Classification public delta only; three format patterns, not full G07."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='3a6e4895f12b8385dbdaf08e131a838701ed4d97'
    scan.OUT=scan.scan.BASE/'PG8986-g07-provenance-public-delta-v1'
    scan.main()
