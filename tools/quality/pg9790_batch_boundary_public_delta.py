"""Preserve independent batch16 original results and new unexecuted boundary Test sources."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '526c0b49fd332a3738f38662a476d585c57370af'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9790-batch-boundary-public-delta-v1'
    scan.main()
