"""Public source/spec delta only, prior to freezing new ordinary pagination tests."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'e4985c3a223c2e48ce66c2ce1672d7840983e1cb'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9659-pagination-source-public-delta-v1'
    scan.main()
