"""Fresh full baseline after exact failed-pair recovery, not old normal completion."""
import pg1388_role_independent_post as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

def payload(seals):
    raw=previous.payload(seals)
    changes=(
        ("{'refs.private.log','before.private.json','prepared.private.json','after.private.json','complete.private'}","{'refs.private.log','before.private.json','prepared.private.json'}"),
        (";closed=json.loads(strict(prepared_root/'after.private.json',0o600,67108864))",''),
        ('require(prepared==closed and initial','require(initial'),
        (" require(strict(prepared_root/'complete.private',0o600,4096)==b'oneBootstrapRolePrepared=true\\nallNewScopesReturnedNormally=true\\nallOriginalValuesPreserved=true\\nstartsStopsReloadsSqlWrites0=true\\n')", " recovered_raw=strict(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1390-prepared-role-fixed-pair-v1/after.private.json'),0o600,67108864)\n require(hashlib.sha256(recovered_raw).hexdigest()=='1e1b3fc3ce6bdf3602e11a8146c6af37a27b5155f12c037e9e9bf81563ea29da');recovered=json.loads(recovered_raw)\n require(recovered['current']==after and recovered['native']==native and recovered['oldNormalClose']is False and recovered['fixedOldJavaHelperGone']is True and recovered['allClientAdvisoryFlocks0']is True)"),
        ("result['preparationNormalClose']=True","result['preparationNormalClose']=False\nresult['failedPairRecovery0']=True"),
        ('pg1388-role-independent-post-v1','pg1391-prepared-role-independent-baseline-v1'),
        ('PG1388-role-independent-post-v1','PG1391-prepared-role-independent-baseline-v1'),
    )
    for old,new in changes:
        if old not in raw:raise ValueError('exact preserved failed phase binding required')
        raw=raw.replace(old,new)
    compile(raw,'<independent created role baseline after failed owner recovery>','exec');return raw

def main():
    if (W/'pg1390-prepared-role-fixed-pair-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual current failed pair recovery required')
    env=dict(previous.previous.previous.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    raw=previous.previous.source().replace('pg1344-current-bootstrap-before-v1','pg1391-prepared-role-independent-baseline-v1')
    exec(compile(raw,'<new created role baseline transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
