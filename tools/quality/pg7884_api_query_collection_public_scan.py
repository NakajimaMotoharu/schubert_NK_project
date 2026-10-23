"""Bounded own public delta, only three known secret formats; no runtime/private inputs."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='f9a0eab86043f59c76d93e7abe426e8fefa0557f'
    scan.OUT=scan.scan.BASE/'PG7884-api-query-collection-public-delta-v1'
    scan.main()
