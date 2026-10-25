"""Include the defect/rollout retest references added after first public delta receipt."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='719e58a0992089a5e52a1c6f3ad96b62fd836258'
    scan.OUT=scan.scan.BASE/'PG9588-web-close-handoff-ledger-public-delta-v1'
    scan.main()
