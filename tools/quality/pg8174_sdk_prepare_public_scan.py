"""Public SDK preparation metadata and exact-source correction; no Jars/private files."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='2bc3399249eb99a1bda0a2d5a61f359c1197383a'
    scan.OUT=scan.scan.BASE/'PG8174-sdk-prepare-public-delta-v1'
    scan.main()
