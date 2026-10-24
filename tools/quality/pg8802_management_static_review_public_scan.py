"""Individual static-review public delta only; no Production/PMD/native replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='1fa09dd369692fcee5e471325641f1ce3715bd48'
    scan.OUT=scan.scan.BASE/'PG8802-management-static-review-public-delta-v1'
    scan.main()
