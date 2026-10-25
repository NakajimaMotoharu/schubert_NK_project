"""Preserve original four-counter success and actual new-Test static failure before correction."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '0002706babad635c5ca7ade76cdbaee134ace432'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9693-semantic-static-failure-public-delta-v1'
    scan.main()
