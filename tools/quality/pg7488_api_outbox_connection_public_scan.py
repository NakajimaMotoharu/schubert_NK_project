"""Necessary changed public source/tool/evidence only, no real service/private input or PT replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='30000ea03'
    scan.OUT=scan.scan.BASE/'PG7488-api-outbox-connection-public-delta-v1'
    scan.main()
