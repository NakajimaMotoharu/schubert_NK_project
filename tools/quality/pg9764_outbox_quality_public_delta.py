"""Public current API count correction qualification, not whole secret/451 gate."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'e598a81bb4200b4e4930278b31479ff927aa025f'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9764-outbox-quality-public-delta-v1'
    scan.main()
