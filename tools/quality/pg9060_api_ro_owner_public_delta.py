"""Current public RO dependency audit delta only, not full G07 or runtime."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='a99721b04f762615b7e6741dfd7b06efd3e11047'
    scan.OUT=scan.scan.BASE/'PG9060-api-ro-owner-public-delta-v1'
    scan.main()
