"""Public component-gate save delta only; no whole secret-gate qualification."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'b5718bcbc30cda9bce5d71e88f34a9418026db4c'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9684-semantic-component-public-delta-v1'
    scan.main()
