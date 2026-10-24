"""Public source/ABI analysis delta only, no private/runtime inputs."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='4b0803fdcb49118e19e07d7871340e045c3d90ef'
    scan.OUT=scan.scan.BASE/'PG8236-histogram-contract-public-delta-v1'
    scan.main()
