"""Public test-only fake-supply delta, not whole G07 or runtime acceptance."""
import pg6990_recovery_public_scan as scan
if __name__=='__main__':
    scan.BEFORE='2e0cc772135d54bdae7d9b45defd228bc1849823'
    scan.OUT=scan.scan.BASE/'PG9220-api-factory-debug-public-delta-v1'
    scan.main()
