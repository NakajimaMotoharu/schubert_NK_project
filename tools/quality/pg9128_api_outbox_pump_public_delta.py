"""Public pump source/PT fixture completion/evidence delta only, not G07 or actual runtime."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='1248ab224f65942a54eb52aca8e41790f6355644'
    scan.OUT=scan.scan.BASE/'PG9128-api-outbox-pump-public-delta-v1'
    scan.main()
