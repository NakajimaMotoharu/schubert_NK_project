"""New source genuine PID1/DONE qualification; captured1321 tuple, not old success."""
import inspect
import pg1117_current_done_probe as transport
from pg1242_fresh_ordinary_done_receipt import payload as previous
from pg1293_completed_unused_stage_sources import SOURCE

CHANGES=[('2914e843f73d48dd93198dbdcae0f735','400b2e34105149ff8f3a11c21da0be6a'),
         ("'100948'","'120359'"),('61234139496','73654946447'),
         ('9f651096-aef9-4fba-90b0-a653e99f035a','d2e3a86f-27a4-4c2a-be21-b512eebf1216'),
         ('2026-10-10T20:03:22.718197Z','2026-10-10T23:30:23.481632Z'),
         ('27accac0-c118-4c98-9244-02625a2d88a7','841b507c-2713-4ffe-8882-68f5fb3f87f5'),
         ('2026, 10, 10, 20, 3, 17','2026, 10, 10, 23, 30, 17'),
         ('pg1242-fresh-ordinary-done-receipt-v1','pg1322-published-root-done-receipt-v1')]


def payload():
    code=previous()
    for old,new in CHANGES:
        if old not in code:raise ValueError('exact captured current Root binding required')
        code=code.replace(old,new)
    compile(code,'<actual current published Root receipt>','exec');return code


def main():
    import json
    live=json.loads((transport.W/'pg1321-live-root-binding-v1.safe.json').read_bytes())
    if live['actualExit']!=0 or live['productionSource']!=SOURCE or live['binding']!={
      'boot':'cbca87383b244090b77cbf029677cdd6','invocation':'400b2e34105149ff8f3a11c21da0be6a','job':'120359','start':73654946447,
      'run':'d2e3a86f-27a4-4c2a-be21-b512eebf1216','cutoff':'2026-10-10T23:30:23.481632Z','activation':'841b507c-2713-4ffe-8882-68f5fb3f87f5'}:
        raise ValueError('actual live capture/current run required')
    code=inspect.getsource(transport.main).replace('pg1112-parent-watch-v1.private.jsonl','pg1318-parent-watch-v1.private.jsonl').replace('pg1117-current-done-receipt-v1','pg1322-published-root-done-receipt-v1').replace('PG1117-current-done-receipt-v1','PG1322-published-root-done-receipt-v1').replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE)
    env=dict(transport.__dict__,payload=payload)
    exec(compile(code,'<new current receipt transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
