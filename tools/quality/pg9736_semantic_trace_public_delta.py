"""Declared current-source SEM trace metadata save only."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'ccd741fe4cd3317d4821dc1c657b749382cfe077'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9736-semantic-trace-public-delta-v1'
    scan.main()
