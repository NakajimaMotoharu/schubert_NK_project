"""One new verify-only normal scope; existing runtime kept byte/inode, writes0."""
import pg1562_pending_runtime_once as prior
from pg1567_existing_runtime_sources import CLASS,TOOLS,SAVE
from pg1568_existing_runtime_compile import valid_frozen
from pg1559_pending_runtime_sources import SOURCE

def valid_receipt(data):
    return type(data)is bytes and data==b'PG1544 STAGE PINNED_SIGNATURE_VERIFIED\nPG1544 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1569_DONE existingRuntimeVerified=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'

def source():
    raw=prior.source()
    for a,b in [('pg1562-pending-runtime-v1',SAVE),('PG1562-pending-runtime-v1','PG1569-existing-runtime-verify-v1'),('pg1560-pending-runtime-frozen-v2.safe.json','pg1568-existing-runtime-frozen-v1.safe.json'),('pg1559-pending-runtime-tools-v2',TOOLS),('Pg1559PendingRuntime',CLASS),("'prepare']","'verify-existing']")]:
        if a not in raw:raise ValueError('fixed verify-only once boundary refused')
        raw=raw.replace(a,b)
    compile(raw,'<once existing canonical runtime verification>','exec');return raw

def main():
    fixed=prior.prior.json.loads((prior.prior.W/'pg1568-existing-runtime-frozen-v1.safe.json').read_bytes())
    if not valid_frozen(fixed):raise ValueError('actual exact verify-only operator required')
    ns={**prior.prior.__dict__,'OUTNAME':'pg1570-existing-runtime-stage-v1','valid_receipt':valid_receipt,'SOURCE':SOURCE}
    exec(compile(source(),'<fresh same runtime normal verification>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
