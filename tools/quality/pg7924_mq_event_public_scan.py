"""Bounded own public delta and three known secret formats, no runtime/private inputs."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='cd3df651c9fb8446e7747d084b1317c4f95fcdfc'
    scan.OUT=scan.scan.BASE/'PG7924-mq-event-public-delta-v1'
    scan.main()
