"""Public same-source pure-predicate qualification, not whole G07 or runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='3359ff3be3dd006f3316b07135f21310e54c3d51'
    scan.OUT=scan.scan.BASE/'PG9292-api-pure-readiness-public-delta-v1'
    scan.main()
