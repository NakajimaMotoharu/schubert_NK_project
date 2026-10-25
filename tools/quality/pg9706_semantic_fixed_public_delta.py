"""Publish only declared fixed-Test evidence delta; not whole G07 scan acceptance."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9706-semantic-fixed-public-delta-v1'
    scan.main()
