"""Necessary changed-public delta only, no runtime/private inputs or old PT replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='d116f054ddf560d9a0bc7409829d3556445ee0bd'
    scan.OUT=scan.scan.BASE/'PG7432-batch-generated-public-delta-v1'
    scan.main()
