"""Public minimal lifetime remedy delta; not full G07/runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='cc1b8796263dca0432701daa05f342b4a3ba8bab'
    scan.OUT=scan.scan.BASE/'PG9242-api-web-life-remedy-public-delta-v1'
    scan.main()
