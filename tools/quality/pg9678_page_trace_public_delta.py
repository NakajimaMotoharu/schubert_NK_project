"""Bounded declared public trace save delta, not whole G07."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '2bd5c2e237d8a6ebe0a77e0b1e72b608ae8c231e'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9678-page-trace-public-delta-v1'
    scan.main()
