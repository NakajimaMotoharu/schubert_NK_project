"""Declared protocol module evidence delta, including honest generated-filter limits."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '9f971c8fd16638f46811a4f10e89297010091ae9'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9730-protocol-module-public-delta-v1'
    scan.main()
