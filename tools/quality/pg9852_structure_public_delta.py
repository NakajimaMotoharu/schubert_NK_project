"""Bounded new public metadata/tool delta only; not full G07 qualification."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '8d23fa17a9976271c0c1d13c2b3afcce4e812f2b'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9852-structure-public-delta-v1'
    scan.main()
