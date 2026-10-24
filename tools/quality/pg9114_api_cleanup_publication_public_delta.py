"""Public cleanup publication delta only; no whole G07 or runtime claim."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='71314afe98b79e0227edf93198c99c57d8affb8f'
    scan.OUT=scan.scan.BASE/'PG9114-api-cleanup-publication-public-delta-v1'
    scan.main()
