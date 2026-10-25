"""Bounded public shape-only residual cache, no new classification or secret-zero claim."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '668384ced1d33a0d075693b96154d8fee5dcafba'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9890-g07-shape-public-delta-v1'
    scan.main()
