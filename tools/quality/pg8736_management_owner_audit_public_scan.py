"""Public ownership audit evidence delta only; no source/runtime acceptance."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='8647974fadc3f0fa1837a9d079317543b0c856ab'
    scan.OUT=scan.scan.BASE/'PG8736-management-owner-audit-public-delta-v1'
    scan.main()
