"""Changed public text only; three known secret formats, never all-secret/runtime claim."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='a605c728706f1c6d50de46ba8c4fda821b0303ce'
    scan.OUT=scan.scan.BASE/'PG7640-api-inbox-replay-public-delta-v1'
    scan.main()
