"""Public policy/trace delta only; not a full secret scan or formal quality gate."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='e14af6f8db69ff877a3af9065d4ad55845c4e1f2'
    scan.OUT=scan.scan.BASE/'PG9342-storage-residual-policy-public-delta-v1'
    scan.main()
