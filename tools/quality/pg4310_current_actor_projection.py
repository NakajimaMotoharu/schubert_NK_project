"""Project pinned private actor facts into bounded public identity data; no operation authority."""
from pg4260_stable_admission_image import execute,SOURCE,BOM

SLOT='pg4310-current-actor-projection-v1'


def payload():
    return 'SOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\n'+r'''
from pathlib import Path
import os,json,hashlib
assert os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
manifest=Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE
p=Path('/var/lib/pgpt-s1-preservation/pg4306-current-failed-authority-read-v1/observed.private.json');raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()=='63269de90bc6bb554e73bde70dcb44bb8e844424c7b364f6597ed1d08aaaf1fd'
v=json.loads(raw);assert v['source']==SOURCE and v['BOM']==BOM;state=v['second']
assert v['first']['actors']==state['actors'] and v['first']['detailedActors']==state['detailedActors']
result={u:{**a,'invocation':state['units'][u]['InvocationID'],'uid':state['detailedActors'][u]['nss']['uid']}for u,a in state['actors'].items()}
assert len(result)==4 and p.read_bytes()==raw
print(json.dumps({'actualExit':0,'source':SOURCE,'BOM':BOM,'actors':result,'referenceSha256':hashlib.sha256(raw).hexdigest(),'historicalCertificateProjectionOnly':True,'currentLivenessOrAuthority':False,'stateChangingActions':0,'formalAccepted':False}))
'''


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(),30))
