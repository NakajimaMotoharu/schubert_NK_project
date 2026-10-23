"""Final HTTP correction public delta only; never runtime/private files or actual secret values."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='b6e20d020fa4d2f2793828c141208adc51ade9cf'
    scan.OUT=scan.scan.BASE/'PG8112-http-duration-final-public-delta-v1'
    scan.main()
