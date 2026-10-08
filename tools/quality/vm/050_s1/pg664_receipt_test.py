"""Unchanged current literal independent PID1/DONE vectors, no VM operations."""
from pathlib import Path

R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=(R/'pg662_receipt_test.py').read_text().replace('pg662_sources','pg664_sources').replace('pg662_parent_receipt','pg664_parent_receipt')
    exec(compile(raw,str(R/'pg664_receipt_test.py'),'exec'),globals())
