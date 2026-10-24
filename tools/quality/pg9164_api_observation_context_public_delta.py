"""Public assembly/source/quality/evidence delta only, not G07/runtime qualification."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='613303252ba6751f6f6b8b8875d86787c40c0a54'
    scan.OUT=scan.scan.BASE/'PG9164-api-observation-context-public-delta-v1'
    scan.main()
