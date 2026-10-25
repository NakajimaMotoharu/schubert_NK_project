"""Bounded public-only save delta; not whole G07 acceptance."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '7bbc3cc5b5215dc297a00da85a9f43882b3252e3'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9672-pagination-public-delta-v1'
    scan.main()
