"""Public API GC selected qualification delta only, no runtime probes."""
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '576ffa194907171defed7a8a5f1f6137de89d2bf'
    scan.OUT = scan.scan.BASE / 'PG8542-api-gc-public-delta-v1'
    scan.main()
