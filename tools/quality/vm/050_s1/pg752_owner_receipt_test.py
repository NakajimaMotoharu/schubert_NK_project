"""Original owner tests plus current literal PID1/DONE; no VM grants."""
from pathlib import Path
from pg752_sources import bind

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=bind((R/'pg717_owner_receipt_test.py').read_text()).replace('pg717_sources','pg752_sources')
    # Independently recorded PID1/Root wall clock for this actual completed parent.
    raw=raw.replace('1791508338000000','1791516640608594')
    raw=raw.replace("done.replace(b'8633b77f', b'old3b77f')", "done.replace(b'55ac70e7', b'oldc70e7')")
    raw=raw.replace("p.bind(p.previous.bind((R / 'pg624_owner_namespace_test.py').read_text()))",
                    "p.bind(p.previous.bind(p.previous.previous.bind((R / 'pg624_owner_namespace_test.py').read_text())))")
    exec(compile(raw,'<actual55ac parent and sealed ownership>','exec'),{'__file__':str(R/'pg752_owner_receipt_test.py'),'__name__':'__main__'})
