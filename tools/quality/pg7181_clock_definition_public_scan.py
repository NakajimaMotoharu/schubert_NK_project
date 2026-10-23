"""Public uncommitted operator/evidence delta since current frozen source, no source/PT replay."""
import pg6990_recovery_public_scan as scan


if __name__=='__main__':
    scan.BEFORE='3b2ef576cf46763d67a9e2914dc547afd2f93ef6'
    scan.OUT=scan.scan.BASE/'PG7181-clock-definition-public-delta-v1'
    scan.main()
