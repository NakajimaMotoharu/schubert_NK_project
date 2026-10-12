"""Actual captured Root13 same-run PID1/DONE oracle, never restart authority."""
import inspect
import json
from pg1701_new_source_done_receipt import payload as previous_payload,EXPECTED as OLD
from pg1700_new_source_live_binding import SOURCE
import pg1601_current_newrun_done_receipt as transport

EXPECTED={'boot':'3d69f5af6bac46b1a5407591c4a79a0d','invocation':'b5a12ee25dc44ec49b08f5d084b4052f','job':'127250','start':81404764713,'run':'4148e3e8-f107-431a-ab27-d6e6d1f1772e','cutoff':'2026-10-12T18:20:32.598894Z','activation':'9adbf05a-61d0-408b-b51d-ab19c7e5b16a'}

def payload():
    raw=previous_payload()
    changes=[(OLD[k],EXPECTED[k])for k in ('invocation','job','run','cutoff','activation')]
    changes += [(str(OLD['start']),str(EXPECTED['start'])),('2026, 10, 12, 14, 19, 26','2026, 10, 12, 18, 20, 30'),('pg1701-new-source-done-receipt-v1','pg1762-next-day-done-receipt-v1')]
    for old,new in changes:
        if old not in raw:raise ValueError('captured binding literal required')
        raw=raw.replace(old,new)
    compile(raw,'<actual Root13 independent PID1 DONE>','exec');return raw

def main():
    engine=transport.prior.transport
    live=json.loads((engine.W/'pg1761-next-day-live-binding-v1.safe.json').read_bytes())
    if live.get('actualExit')!=0 or live.get('productionSource')!=SOURCE or live.get('binding')!=EXPECTED:raise ValueError('exact actually captured Root13 binding required')
    raw=inspect.getsource(engine.main).replace('pg1112-parent-watch-v1.private.jsonl','pg1758-parent-watch-v1.private.jsonl').replace('pg1117-current-done-receipt-v1','pg1762-next-day-done-receipt-v1').replace('PG1117-current-done-receipt-v1','PG1762-next-day-done-receipt-v1').replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE)
    ns={**engine.__dict__,'payload':payload}
    exec(compile(raw,'<Root13 readonly DONE transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
