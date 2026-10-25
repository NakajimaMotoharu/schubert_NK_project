"""Declared cleanup value Test/host proof delta only, not a whole-repository G07 acceptance."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9826-cleanup-public-delta-v1'
    scan.main()
