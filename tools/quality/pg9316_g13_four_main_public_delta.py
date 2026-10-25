"""Bounded four-main metadata delta only; no new whole-repository scanner."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='055734c6780a16a7193e44c1e507ef3a7481a8aa'
    scan.OUT=scan.scan.BASE/'PG9316-g13-four-main-public-delta-v1'
    scan.main()
