"""Preserve original three PT successes and failed static input before classpath correction."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '3154be39380de4771111f859ffb8315420274b0a'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9667-pagination-static-failure-public-delta-v1'
    scan.main()
