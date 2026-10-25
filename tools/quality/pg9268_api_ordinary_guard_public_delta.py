"""Public same-source ordinary qualification delta, not full G07/runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='2145e20cfd7bfdcbc14240d8af95d6b75bf16da0'
    scan.OUT=scan.scan.BASE/'PG9268-api-ordinary-guard-public-delta-v1'
    scan.main()
