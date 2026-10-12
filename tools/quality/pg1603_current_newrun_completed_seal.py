"""Current noargs genuine DONE / full private seal / independent SQL oracle.

NK-OPS-001; SS341/343/353; PT-DEP-1603001. Data capture only: no start,
stop, reload, credential disclosure or Production expected-value generation.
"""
import inspect
import pg1578_current_completed_seal as prior
from pg1601_current_newrun_done_receipt import payload as receipt
from pg1602_current_newrun_rows_oracle import source as oracle

OWNED={
    'artemis.service':('216143','db75a3f0c2494fdea570b30012a5b871',3857194,'2a7089f6e2bbbbe31a74253fab119bd63b0055019e386c3a6f372a19d6e004b6'),
    'schubert-nk-api.service':('256734','994fd53232ee426d9ca93a2f311bda53',3946268,'68f3cbf97eadad32b0b268bd6372d40ea12a88b60004eae1913099664a8fe3e0'),
    'schubert-nk-web.service':('257744','7a75a61efae5403692eb523eea322c19',3947570,'838017475d17da509bb856c8e3a1a0bf7b24b97ed445cd00b60536407897b142'),
    'caddy.service':('259611','99a144b6cba34d9e8ebdbfad060302de',3950544,'8ffd9e85b36aeea3c9aee774d9953a1c3ec022b925b0d413ad644e9d53ce9c0a')}

def once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('new-run finite source boundary refused')
    return raw.replace(old,new)

def payload():
    raw=prior.payload()
    guard=receipt();guard=guard[:guard.index("private=Path('/var/lib/pgpt-s1-preservation/pg1601-current-newrun-done-receipt-v1')")]
    oldguard=prior.receipt();oldguard=oldguard[:oldguard.index("private=Path('/var/lib/pgpt-s1-preservation/pg1577-current-root-done-receipt-v1')")]
    raw=once(raw,'GUARD='+repr(oldguard),'GUARD='+repr(guard))
    raw=once(raw,'OWNED='+repr(prior.OWNED),'OWNED='+repr(OWNED))
    for old,new in [('pg1578-current-completed-seal-v1','pg1603-current-newrun-completed-seal-v1'),('pg1573-current-resume-once-v1/before.private.json','pg1596-current-ordinary-before-v1/before.private.json'),('cc8ec852ca75bb2cf980ec97176ec771dab17bc0ffa4b3c2936f1c76db93345d','6d144309d3294abb31440d523940bfd4275d3a99eab3e4ce8e0486f81a154bce'),('15700a87-9117-4f63-a0ff-768dd604d0f1','0be226b1-bbb7-43d3-aa9e-59d0bda70f9a'),('2026-10-11T21:18:59.040097Z','2026-10-12T06:23:13.176261Z'),('9e706936-a3c9-4a09-bb66-e2b1e8bbef66','d28eead2-941c-4b97-9747-1758c0809e29')]:
        raw=raw.replace(old,new)
    raw=once(raw,"require(proof.result['endMonotonicUs']==33583425972 and proof.result['elapsedSeconds']==1539.994702)","require(0<proof.result['elapsedSeconds']<=1800)")
    raw=once(raw,"require(set(rs)==set(before['rows'])and len(rs)==24)","require(set(rs)==set(before['rows'])and len(rs)==24)\n business=types.ModuleType('independent_sql');exec(ORACLE,business.__dict__);business_result=business.qualify(before['rows'],rs,'2026-10-12T06:23:13.176261Z',proof.done.decode('ascii').splitlines()[4])")
    # The independently qualified receipt's schema is fixed by PT-DEP-1601.
    raw=raw.replace("'businessFullOraclePending':True","'businessFullOraclePending':False,'businessOracle':business_result")
    # Outside capture, use its returned oracle result rather than a local name.
    raw=raw.replace("'businessOracle':business_result,'formalAccepted'","'businessOracle':current['businessOracle'],'formalAccepted'")
    raw='ORACLE='+repr(oracle())+'\n'+raw
    compile(raw,'<current noargs fullseal independent SQL>','exec');return raw

def main():
    raw=inspect.getsource(prior.main).replace('pg1578-current-completed-seal-v1','pg1603-current-newrun-completed-seal-v1').replace('pg1577-current-root-done-receipt-v1','pg1601-current-newrun-done-receipt-v1')
    ns={**prior.__dict__,'payload':payload};exec(compile(raw,'<current noargs fullseal transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
