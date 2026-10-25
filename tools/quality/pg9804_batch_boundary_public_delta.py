"""Declared batch boundary qualification text save, not a whole secret or formal gate."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '58913ab374ef54d138fa3fad8c80cccd03d87c10'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9804-batch-boundary-public-delta-v1'
    scan.main()
