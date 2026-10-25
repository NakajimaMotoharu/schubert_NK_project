"""Bounded four-library preflight delta only; never full G07 or secret-zero acceptance."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'e0ec18b22cd5ad299a2f0e0e98684fb4b2a342c9'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9862-library-preflight-public-delta-v1'
    scan.main()
