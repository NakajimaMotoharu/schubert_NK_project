"""Independent full originals/resources and SSC263 finite role delta; new ADMIN baseline."""
import inspect
import json
import pg1344_bootstrap_before as previous
import pg1369_bootstrap_role_policy as policy
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

def payload(seals):
    raw=previous.payload(seals)
    frozen=json.loads((W/'pg1385-frozen-v2.safe.json').read_bytes())
    raw=raw.replace('bus=dbus.SystemBus(private=True);', 'import types\nrole_policy=types.ModuleType("independent_role_policy");exec('+repr(inspect.getsource(policy))+',role_policy.__dict__)\nROLE_HASHES='+repr(frozen['fileHashes'])+'\nbus=dbus.SystemBus(private=True);')
    marker=' native=snapshot();require(native==snapshot())'
    if raw.count(marker)!=1:raise ValueError('one fresh full native snapshot required')
    raw=raw.replace(marker,marker+'''
 prepared_root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1380-bootstrap-role-prepare-v1')
 require({p.name for p in prepared_root.iterdir()}=={'refs.private.log','before.private.json','prepared.private.json','after.private.json','complete.private'})
 for p in prepared_root.iterdir():require(metadata(p)[2:5]==[0,0,stat.S_IFREG|0o600]and p.lstat().st_nlink==1)
 initial=json.loads(strict(prepared_root/'before.private.json',0o600,67108864));prepared=json.loads(strict(prepared_root/'prepared.private.json',0o600,67108864));closed=json.loads(strict(prepared_root/'after.private.json',0o600,67108864))
 require(prepared==closed and initial['current']==prepared['current']==after and prepared['native']==native)
 original_raw=strict(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1344-current-bootstrap-before-v1/after.private.json'),0o600,67108864)
 require(hashlib.sha256(original_raw).hexdigest()=='f64ed4689d2c52e2227f771f7870414686ff0e6f52a6dc7b3d1b22313668428d'and json.loads(original_raw)['native']==initial['native'])
 role_policy.delta(initial['native'],native,prepared['startNs'],prepared['endNs'])
 require(strict(prepared_root/'complete.private',0o600,4096)==b'oneBootstrapRolePrepared=true\\nallNewScopesReturnedNormally=true\\nallOriginalValuesPreserved=true\\nstartsStopsReloadsSqlWrites0=true\\n')
 role=pathlib.Path(role_policy.ROOT,role_policy.ROLE);require(not list(role.iterdir())and not os.listxattr(role)and command(['findmnt','--target',str(role),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
 require(command(['id','-u','schubert-api']).strip()==b'999'and command(['id','-g','schubert-api']).strip()==b'981')
 tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1380-bootstrap-role-tools-v2');require({str(p.relative_to(tools))for p in tools.rglob('*')if p.is_file()}==set(ROLE_HASHES)|{'payload-sha256.json'})
 for name,digest in ROLE_HASHES.items():require(hashlib.sha256(strict(tools/name,0o400,67108864)).hexdigest()==digest)
 require(json.loads(strict(tools/'payload-sha256.json',0o400,67108864))==ROLE_HASHES)
''')
    raw=raw.replace('pg1344-current-bootstrap-before-v1','pg1388-role-independent-post-v1').replace('PG1344-current-bootstrap-before-v1','PG1388-role-independent-post-v1')
    # The old immutable before reference must not be renamed to the new result slot.
    raw=raw.replace("pathlib.Path('/var/lib/pgpt-s1-preservation/pg1388-role-independent-post-v1/after.private.json')","pathlib.Path('/var/lib/pgpt-s1-preservation/pg1344-current-bootstrap-before-v1/after.private.json')")
    marker="result['batchRows']=len(value['rows']['schubert.batch_runs'])"
    raw=raw.replace(marker,marker+"\nresult['oneBootstrapRolePrepared']=True\nresult['allOriginalNativeEntriesPreserved']=True\nresult['nativeNodes']=len(native)\nresult['preparationNormalClose']=True")
    compile(raw,'<independent full role delta post>','exec');return raw

def main():
    if (W/'pg1387-prepare-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual normal corrected role preparation required')
    env=dict(previous.previous.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    raw=previous.source().replace('pg1344-current-bootstrap-before-v1','pg1388-role-independent-post-v1')
    exec(compile(raw,'<new role post transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
