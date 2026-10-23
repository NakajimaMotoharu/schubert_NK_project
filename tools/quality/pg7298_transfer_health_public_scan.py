"""Final changed public record delta, three known formats only, no actual runtime scan."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='3343f93324a37244a654e92a43910d723bce0ab4'
    scan.OUT=scan.scan.BASE/'PG7298-transfer-health-public-delta-v1'
    scan.main()
