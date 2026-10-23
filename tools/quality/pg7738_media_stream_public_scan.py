"""Own public delta only; three known secret formats, never private/runtime logs."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='b798f17e46b3c48f7542035b52ed8edbc7be40d1'
    scan.OUT=scan.scan.BASE/'PG7738-media-stream-public-delta-v1'
    scan.main()
