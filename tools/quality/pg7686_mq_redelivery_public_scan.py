"""Own public text delta and three known secret formats only; no private/runtime claim."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='6efb70c2d5e8e8e2221084b8c0926bc157e445c1'
    scan.OUT=scan.scan.BASE/'PG7686-mq-redelivery-public-delta-v1'
    scan.main()
