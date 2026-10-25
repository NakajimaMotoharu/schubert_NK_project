"""Six shared-oracle support owner metadata/tool delta, not whole repository G07 acceptance."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '223bbcef6'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9840-shared-probe-public-delta-v1'
    scan.main()
