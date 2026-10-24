"""Ancestor provenance public delta only; not whole G07 or history secret gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='a2e40a335ad64fb1a7165878c2d7fcbafa8317ee'
    scan.OUT=scan.scan.BASE/'PG8996-g07-ancestor-public-delta-v1'
    scan.main()
