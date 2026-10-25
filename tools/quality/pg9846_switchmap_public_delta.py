"""Bounded public delta only; not full G07 or generated-code acceptance."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '810f82485448c37e82629b0bca544f95d52d8a46'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9846-switchmap-public-delta-v1'
    scan.main()
