"""Public worker/quality/evidence delta only; neither G07 qualification nor actual runtime."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='022214cdcc19e88228f46ce6d430c57fb6ef0aed'
    scan.OUT=scan.scan.BASE/'PG9142-api-observation-worker-public-delta-v1'
    scan.main()
