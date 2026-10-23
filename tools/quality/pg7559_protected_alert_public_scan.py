"""Only declared changed public text, three known formats; no private/runtime input."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='350cf103c'
    scan.OUT=scan.scan.BASE/'PG7559-protected-alert-public-delta-v1'
    scan.main()
