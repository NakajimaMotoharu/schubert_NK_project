"""Declared public MQ SDK and host lint cleanup delta; no target/private data."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='1b31b4a6c900352445e6a737ff0ba9965880cf86'
    scan.OUT=scan.scan.BASE/'PG8194-mq-prometheus-public-delta-v1'
    scan.main()
