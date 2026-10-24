"""Declared API counter repair/public diagnostic/quality delta, never target/private data."""
import pg6990_recovery_public_scan as scan

if __name__=='__main__':
    scan.BEFORE='54df143dc9a4f12dcf9783aa86a8b94e9144636f'
    scan.OUT=scan.scan.BASE/'PG8222-api-counter-public-delta-v1'
    scan.main()
