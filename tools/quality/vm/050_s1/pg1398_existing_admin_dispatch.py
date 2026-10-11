"""One new existing ADMIN stage/verify/execute bound to current normal role and old failures."""
from pathlib import Path
import pg1358_current_bootstrap_dispatch as previous
R=Path(__file__).resolve().parent

def source():
    raw=previous.source().replace('Pg1356','Pg1396').replace('pg1356','pg1396')
    raw=raw.replace('pg1355-bootstrap-fixed-handoff-v2','pg1390-prepared-role-fixed-pair-v1').replace('pg1348-verify-v3','pg1387-prepare-v1')
    raw=raw.replace('pg1344-current-bootstrap-before-v1','pg1395-existing-role-normal-post-v1')
    marker="    assert(W/'pg1395-existing-role-normal-post-v1.exit').read_bytes()==b'0\\n'"
    if raw.count(marker)!=1:raise ValueError('one normal role fullpost qualification required')
    raw=raw.replace(marker,marker+"\n    role=json.loads((W/'pg1395-existing-role-normal-post-v1.safe.json').read_bytes());assert role['existingRoleVerificationNormalClose']is True and role['allClientAdvisoryFlock0']is True and role['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'")
    compile(raw,'<new qualified ADMIN once-only transport>','exec');return raw

if __name__=='__main__':exec(compile(source(),'<new ADMIN dispatch>','exec'),{'__file__':str(R/'pg1398_existing_admin_dispatch.py'),'__name__':'__main__'})
