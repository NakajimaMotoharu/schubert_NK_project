"""Own public delta only; three known secret formats, no private/runtime inputs."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='24b0a9c9c'
    scan.OUT=scan.scan.BASE/'PG7782-media-bytes-public-delta-v1'
    scan.main()
