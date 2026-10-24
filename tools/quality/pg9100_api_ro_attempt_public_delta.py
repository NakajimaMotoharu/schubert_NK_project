"""RO attempt source/failure/success/public record delta only, not full G07 or runtime."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='c0fb2203f'
    scan.OUT=scan.scan.BASE/'PG9100-api-ro-attempt-public-delta-v1'
    scan.main()
