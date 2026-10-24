"""Refresh/HTTP scoped quality public delta only; no whole451 or runtime claims."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='6a0bfd0edcf902117f3dbe30399c0be7082677ec'
    scan.OUT=scan.scan.BASE/'PG8828-metric-refresh-public-delta-v1'
    scan.main()
