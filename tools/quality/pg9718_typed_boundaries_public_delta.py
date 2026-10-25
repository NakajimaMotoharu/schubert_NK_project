"""Bounded public typed quality-save delta only."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '7a3936d74adf123582dc0e312c9c39998c19c5f6'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9718-typed-boundaries-public-delta-v1'
    scan.main()
