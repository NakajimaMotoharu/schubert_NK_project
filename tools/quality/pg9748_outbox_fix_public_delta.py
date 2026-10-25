"""Preserve recorded pre-fix failure plus untested count invariant correction."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '303d1a7f44e02829df0781c9a0d63857c81602db'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9748-outbox-fix-public-delta-v1'
    scan.main()
