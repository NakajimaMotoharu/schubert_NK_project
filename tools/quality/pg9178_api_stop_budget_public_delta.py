"""Public primitive-budget/source/quality delta only, neither full G07 nor runtime qualification."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='0910f0706d6767fd5002efa75a30e110223f295a'
    scan.OUT=scan.scan.BASE/'PG9178-api-stop-budget-public-delta-v1'
    scan.main()
