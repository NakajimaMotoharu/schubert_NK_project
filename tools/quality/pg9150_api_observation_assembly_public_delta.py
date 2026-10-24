"""Public dependency audit delta only, no G07 qualification."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='fcf3b0d4a5cd8ea54142072e90f307b06eeb5c26'
    scan.OUT=scan.scan.BASE/'PG9150-api-observation-assembly-public-delta-v1'
    scan.main()
