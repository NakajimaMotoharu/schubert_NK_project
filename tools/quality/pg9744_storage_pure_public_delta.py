"""Declared pure storage host evidence delta, not full G07 qualification."""
from pathlib import Path
import pg6990_recovery_public_scan as scan

if __name__ == '__main__':
    scan.BEFORE = '95102e7230be11630cbb078bb347c48114ba61ec'
    scan.OUT = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9744-storage-pure-public-delta-v1'
    scan.main()
