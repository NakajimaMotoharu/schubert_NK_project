"""Only nonblocking public clarification and checkpoint; never release or probe an operation HOLD."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='4e3186e9da255699eef1a597cc5cecbb066c7b60'
    scan.OUT=scan.scan.BASE/'PG9626-qa053-public-delta-v1'
    scan.main()
