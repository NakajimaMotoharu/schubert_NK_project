"""Declared current batch Test-owner overlay and append-only quota correction evidence."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'e8b43eda3a74e2c4ef56436bfa14cc5227207823'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9810-batch-trace-public-delta-v1'
    scan.main()
