"""Read-only gap-map document/tool/evidence delta only, never whole G07 qualification."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'e26151435687081ccf0bdc5cbf7a761476871bb6'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9832-gap-map-public-delta-v1'
    scan.main()
