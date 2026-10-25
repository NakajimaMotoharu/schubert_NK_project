"""Public source-contract diagnosis only, not full G07 or runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='a98ca1135d4da97d4329cd9b2c18e8339c0bd200'
    scan.OUT=scan.scan.BASE/'PG9228-api-life-legacy-public-delta-v1'
    scan.main()
