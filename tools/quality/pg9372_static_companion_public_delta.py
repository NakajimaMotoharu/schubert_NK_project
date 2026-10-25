"""Bounded public static-trace evidence only, not whole secret/production quality acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='767b5396ab7802864358617e029b7988dc2fcbfa'
    scan.OUT=scan.scan.BASE/'PG9372-static-companion-public-delta-v1'
    scan.main()
