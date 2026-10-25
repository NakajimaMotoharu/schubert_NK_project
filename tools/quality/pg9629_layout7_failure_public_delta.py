"""Preserve failed first Layout7 aggregate and QA053 partial answer before correction."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '515178611958f4643d4f5f466436bcac36a6ee4d'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9629-layout7-first-failure-public-delta-v1'
    scan.main()
