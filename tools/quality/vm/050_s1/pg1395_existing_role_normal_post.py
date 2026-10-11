"""Independent original finite delta plus genuinely normal read-only verifier receipts."""
import json
import pg1391_prepared_role_independent_baseline as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

def payload(seals):
    raw=previous.payload(seals)
    hashes=json.loads((W/'pg1393-frozen-v2.safe.json').read_bytes())['fileHashes']
    marker=" require(recovered['current']==after and recovered['native']==native and recovered['oldNormalClose']is False and recovered['fixedOldJavaHelperGone']is True and recovered['allClientAdvisoryFlocks0']is True)"
    if raw.count(marker)!=1:raise ValueError('one exact failed recovery join required')
    raw=raw.replace(marker,marker+'''
 verified_root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1392-bootstrap-role-prepare-v1')
 require({p.name for p in verified_root.iterdir()}=={'refs.private.log','before.private.json','prepared.private.json','after.private.json','complete.private'})
 for p in verified_root.iterdir():require(metadata(p)[2:5]==[0,0,stat.S_IFREG|0o600]and p.lstat().st_nlink==1)
 verified_initial=json.loads(strict(verified_root/'before.private.json',0o600,67108864));verified_prepared=json.loads(strict(verified_root/'prepared.private.json',0o600,67108864));verified_closed=json.loads(strict(verified_root/'after.private.json',0o600,67108864))
 require(verified_prepared==verified_closed and verified_initial['current']==verified_prepared['current']==after and verified_initial['native']==verified_prepared['native']==native)
 require(strict(verified_root/'complete.private',0o600,4096)==b'oneBootstrapRoleVerified=true\\nallNewScopesReturnedNormally=true\\nallOriginalValuesPreserved=true\\nstartsStopsReloadsSqlWrites0=true\\n')
''')
    raw=raw.replace('ROLE_HASHES='+repr(json.loads((W/'pg1385-frozen-v2.safe.json').read_bytes())['fileHashes']),'ROLE_HASHES='+repr(hashes))
    raw=raw.replace("tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1380-bootstrap-role-tools-v2')","tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1392-bootstrap-role-tools-v2')")
    raw=raw.replace('pg1391-prepared-role-independent-baseline-v1','pg1395-existing-role-normal-post-v1').replace('PG1391-prepared-role-independent-baseline-v1','PG1395-existing-role-normal-post-v1')
    raw=raw.replace("result['failedPairRecovery0']=True","result['failedPairRecovery0']=True\nresult['existingRoleVerificationNormalClose']=True")
    compile(raw,'<full normal existing role independent post>','exec');return raw

def main():
    if (W/'pg1394-prepare-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual new existing-role verifier normal completion required')
    env=dict(previous.previous.previous.previous.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    raw=previous.previous.previous.source().replace('pg1344-current-bootstrap-before-v1','pg1395-existing-role-normal-post-v1')
    exec(compile(raw,'<normal existing-role full post transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
