"""Bounded source/spec/witness delta before a new candidate source freeze."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '8da36c9e4'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9865-nonce-source-public-delta-v1'
    scan.main()
