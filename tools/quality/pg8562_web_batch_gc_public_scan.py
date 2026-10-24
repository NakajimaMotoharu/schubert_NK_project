"""Public role-local GC PT/quality and selection-tool repair delta only."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '21702d7c3adcf3198d27acefd2dddbe2281eac19'
    scan.OUT = scan.scan.BASE / 'PG8562-web-batch-gc-public-delta-v1'
    scan.main()
