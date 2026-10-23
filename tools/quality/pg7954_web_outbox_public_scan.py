"""Bounded own public delta and three known secret formats, never private runtime inputs."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='8e540d3b29b5e1b28ffe69911b13720bb0aba1f7'
    scan.OUT=scan.scan.BASE/'PG7954-web-outbox-public-delta-v1'
    scan.main()
