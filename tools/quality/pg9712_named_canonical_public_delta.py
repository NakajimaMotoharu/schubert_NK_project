"""Save only declared named component source/evidence delta, no whole G07 claim."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '50f96de0a452057bd7573db1bb3a6fdbbd45ff5f'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9712-named-canonical-public-delta-v1'
    scan.main()
