"""Read current metadata-only owner and original completed post; no operations."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg4490_inspect_pair_handoff_sources as original
from pg1446_current_cold_stage import W,SSH
from pg4434_current_candidate_admission_read import authenticate_host


def payload():
    raw=original.payload();marker='import sys,time,signal,select,dbus,traceback'
    if raw.count(marker)!=1:raise ValueError('one fixed complete read prelude')
    raw=raw[:raw.index(marker)]+BODY
    if check(raw,'<metadata-only full post read>'):raise ValueError('all emitted static0')
    return raw


BODY=r'''
save=base/'pg4504-post-retainer-full-read-v1';save.mkdir(mode=0o700)
oldmeta=Path('/proc/828676');child=Path('/proc/829193')
def terminal():
 raw=(child/'stat').read_text();f=raw.rsplit(')',1)[1].split()
 require(f[0]=='Z'and int(f[1])==828676 and not(child/'cmdline').read_bytes()and not list((child/'fd').iterdir()))
 return {'pid':829193,'ticks':int(f[19]),'state':f[0],'ppid':int(f[1]),'rawWaitStatus':int(f[49]),'statSha256':hashlib.sha256(raw.encode()).hexdigest()}
a=proc(828676);ash=private('first-owner.private.json',a);c=terminal();csh=private('first-terminal.private.json',c)
first=snapshot();fsh=private('first-data.private.json',first);cfg=config();cfgsh=private('first-config.private.json',cfg)
b=proc(828676);bsh=private('second-owner.private.json',b);d=terminal();dsh=private('second-terminal.private.json',d)
second=snapshot();ssh=private('second-data.private.json',second);cfg2=config();cfg2sh=private('second-config.private.json',cfg2)
require(a==b and a['ticks']==16705476 and a['argvSha256']=='51c27aa637200ae1f7a30fccb7dd27511286366392131c40edf7fde823787349'and a['children']==[829193])
require(c==d and c['rawWaitStatus']==0 and first==second and cfg==cfg2)
require(first['database']['peers']==[]and first['database']['locks']==[]and first['flocks']==[])
post=base/'pg4490-inspect-pair-handoff-v2-independent-post';receipt=(post/'manifest.safe.json').read_bytes();require(hashlib.sha256(receipt).hexdigest()=='7ab5cdc6f68904cd44fcd42aa1e64009f679b3ed6acb59b853ba68a79e0bc55a')
value=json.loads(receipt);require(value['actualExit']==0 and value['newMARDDBTenRefNormalClose']is True and value['beforeSha256']==value['afterSha256']=='148a8d8a3a3284dbf4a72833ca808ca8a07cee84a85b5562f07356006ac91148')
identity={'exe':str((oldmeta/'exe').readlink()),'root':str((oldmeta/'root').readlink()),'cwd':str((oldmeta/'cwd').readlink())};ish=private('identity.private.json',identity)
sealed=base/'pg480-backup-tools-v3/pg480_backup_refs.py';code=sealed.read_bytes();require(hashlib.sha256(code).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
with(save/'sealed-reference.private.py').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(code);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':data['source']['commit'],'BOM':sha,'boot':boot,
 'ownerSha256':ash,'ownerSecondSha256':bsh,'terminalSha256':csh,'terminalSecondSha256':dsh,'dataSha256':fsh,'secondDataSha256':ssh,'configurationSha256':cfgsh,'secondConfigurationSha256':cfg2sh,
 'identitySha256':ish,'owner':{'pid':828676,'ticks':16705476,'argvSha256':a['argvSha256'],'fdCount':len(a['fds']),'authority':a['authority'],'cgroup':a['cgroup'],'fdTargets':{k:v['target']for k,v in a['fds'].items()}},
 'terminal':c,'independentPostCompleted0':True,'allNewPostScopesNormal':True,'retainerScopeNormal':False,'operationsIssued':0,'formalAccepted':False}))
'''


def main():
    raw=payload();authenticate_host();os.umask(0o077);out=W/'pg4504-post-retainer-full-read-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'operationsIssued':0}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
    if result.returncode==0:
        r=subprocess.run(SSH+['sudo','-n','cat','/var/lib/pgpt-s1-preservation/pg4504-post-retainer-full-read-v1/sealed-reference.private.py'],capture_output=True,timeout=30)
        if r.returncode!=0 or hashlib.sha256(r.stdout).hexdigest()!='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7':raise ValueError('fixed private sealed source')
        (out/'sealed-reference.private.py').write_bytes(r.stdout)
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
