"""Actual PG1573 PID1/DONE/currentGC independent receipt; no root/stop authority."""
import inspect
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
import pg1117_current_done_probe as transport
from pg1322_published_root_done_receipt import payload as previous

SOURCE='4d6bcbddb417b76d27e52d5d9640752c300edccf'

def payload():
    s=previous()
    for a,b in [('cbca87383b244090b77cbf029677cdd6','3d69f5af6bac46b1a5407591c4a79a0d'),('400b2e34105149ff8f3a11c21da0be6a','c52c914a72804a89b0fd5f252f6ac0fc'),("'120359'","'50856'"),('73654946447','32043431270'),('d2e3a86f-27a4-4c2a-be21-b512eebf1216','15700a87-9117-4f63-a0ff-768dd604d0f1'),('2026-10-10T23:30:23.481632Z','2026-10-11T21:18:59.040097Z'),('841b507c-2713-4ffe-8882-68f5fb3f87f5','9e706936-a3c9-4a09-bb66-e2b1e8bbef66'),('2026, 10, 10, 23, 30, 17','2026, 10, 11, 21, 18, 57'),('pg1322-published-root-done-receipt-v1','pg1577-current-root-done-receipt-v1')]:
        if a not in s:raise ValueError('actual fresh captured receipt binding required')
        s=s.replace(a,b)
    compile(s,'<actual current PID1/DONE independent receipt>','exec');return s

def main():
    raw=inspect.getsource(transport.main).replace('pg1112-parent-watch-v1.private.jsonl','pg1572-parent-watch-v1.private.jsonl').replace('pg1117-current-done-receipt-v1','pg1577-current-root-done-receipt-v1').replace('PG1117-current-done-receipt-v1','PG1577-current-root-done-receipt-v1').replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE)
    ns={**transport.__dict__,'payload':payload};exec(compile(raw,'<actual current root receipt transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
