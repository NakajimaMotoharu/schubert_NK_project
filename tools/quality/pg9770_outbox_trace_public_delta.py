"""Declared current-source Outbox trace overlay save, not product acceptance."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = 'b9ad40f37a1391cf70073861a95a9a0a3dc22173'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9770-outbox-trace-public-delta-v1'
    scan.main()
