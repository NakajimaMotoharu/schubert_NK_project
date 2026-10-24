"""Public Web/Batch owner implementation and same-source quality delta only."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='cbee50dacaab3c4db3eb2edab747f406267606e3'
    scan.OUT=scan.scan.BASE/'PG8718-web-batch-standard-source-public-delta-v1'
    scan.main()
