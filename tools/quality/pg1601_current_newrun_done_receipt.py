"""Current ordinary new-run generation PID1/DONE oracle; never Root authority."""
import inspect
import pg1577_current_root_done_receipt as prior

def payload():
    raw=prior.payload()
    for old,new in [('c52c914a72804a89b0fd5f252f6ac0fc','e4d891c38dde4e16a5c848e23ef3f83c'),("'50856'","'71184'"),('32043431270','38365395523'),('15700a87-9117-4f63-a0ff-768dd604d0f1','0be226b1-bbb7-43d3-aa9e-59d0bda70f9a'),('2026-10-11T21:18:59.040097Z','2026-10-12T06:23:13.176261Z'),('9e706936-a3c9-4a09-bb66-e2b1e8bbef66','d28eead2-941c-4b97-9747-1758c0809e29'),('2026, 10, 11, 21, 18, 57','2026, 10, 12, 6, 23, 10'),('pg1577-current-root-done-receipt-v1','pg1601-current-newrun-done-receipt-v1')]:
        if old not in raw:raise ValueError('actual captured newrun binding absent')
        raw=raw.replace(old,new)
    compile(raw,'<actual current newrun independent PID1 DONE>','exec');return raw

def main():
    raw=inspect.getsource(prior.transport.main).replace('pg1112-parent-watch-v1.private.jsonl','pg1597-parent-watch-v1.private.jsonl').replace('pg1117-current-done-receipt-v1','pg1601-current-newrun-done-receipt-v1').replace('PG1117-current-done-receipt-v1','PG1601-current-newrun-done-receipt-v1').replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed',prior.SOURCE)
    ns={**prior.transport.__dict__,'payload':payload};exec(compile(raw,'<actual captured newrun receipt transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
