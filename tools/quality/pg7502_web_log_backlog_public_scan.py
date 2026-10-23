"""Necessary public changed-source/tool/evidence delta only; no private/runtime inputs or PT replay."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='ac18570dc'
    scan.OUT=scan.scan.BASE/'PG7502-web-log-backlog-public-delta-v1'
    scan.main()
