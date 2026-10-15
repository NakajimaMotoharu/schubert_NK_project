"""Separate RO whole-post and closed current-cohort native capsule extraction.

451/SS343/355/PT-OPS-LFACT-POST001. No start/stop/deploy, no failed stream.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from pyflakes.api import check
import pg3216_legacy_negative_dispatch as transport
from pg1446_current_cold_stage import W

OUT = W / 'pg3226-legacy-negative-post-v1'
CODE = r'''
import hashlib,io,json,os,stat,sys,tarfile,time
from pathlib import Path
os.umask(0o077)
STAGE=Path('/home/ubuntu/pg3224-legacy-negative-v1')
for name,digest in HASHES.items():
 p=STAGE/name;s=p.lstat()
 assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o400 and hashlib.sha256(p.read_bytes()).hexdigest()==digest
sys.path.insert(0,str(STAGE))
import pg3216_legacy_negative_observer as o
import pg3218_legacy_negative_retained as c
o.guard();c.runtime_fixed();root=o.BASE/'observer-cohort-v3'
whole=json.loads((root/'manifest.safe.json').read_bytes())
o.require(whole['actualExit']==0 and whole['cases']==7 and whole['source']==o.SOURCE and whole['boot']==o.BOOT and whole['naturalUnitExit']==0 and not(root/'failed.safe.json').exists())
before=json.loads((root/'before.private.json').read_bytes())
o.require(o.tree()==before['tree']and o.database()==before['database']and o.stable_bad()==before['bad'])
units={}
for name in ['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service',o.UNIT,'schubert-nk-bootstrap-admin.service']:
 text=o.command(['systemctl','show',name,'-p','ActiveState','-p','SubState','-p','MainPID','-p','ControlPID','-p','Job']).stdout
 v=dict(line.split('=',1)for line in text.splitlines())
 o.require(v=={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':''})
 p=Path('/sys/fs/cgroup/system.slice')/name
 o.require(not p.exists()or not(p/'cgroup.procs').read_text().strip());units[name]=v
o.require(not Path('/proc',str(whole['pid'])).exists())
stop=json.loads((root/'owned-stop.safe.json').read_text());o.require(stop['actualExit']==0 and stop['invocation']==whole['invocation'])
methods=[json.loads(line)for line in(root/'bus.private.jsonl').read_text().splitlines()]
mutations=[x for x in methods if x['member']not in ['GetUnit','LoadUnit','GetUnitByPID','Subscribe','Unsubscribe']]
o.require([x['member']for x in mutations]==['StartUnit','StopUnit']and all(x['payload']['data']==[o.UNIT,'replace']for x in mutations))
meta=(o.BASE/'runtime/input.safe.json').read_bytes();files={'runtime-input.safe.json':meta}
for test in o.IDS:
 observed=(root/(test+'.observer.safe.json')).read_bytes();v=json.loads(observed)
 case=(o.BASE/'case-cohort-v3'/(test+'.safe.json')).read_bytes();a=json.loads(case)
 o.require(v['testId']==a['testId']==test and v['actualExit']==0 and a['status']=='PASS'and v['approvalAccessObserved']and a['source']==o.SOURCE)
 files['observer/'+test+'.safe.json']=observed;files['case/'+test+'.safe.json']=case
for name in ['manifest.safe.json','setup.safe.json','owned-stop-reservation.safe.json','owned-stop.safe.json']:
 files[name]=(root/name).read_bytes()
native=o.BASE/'cohort-native-v3.exec';ns=native.lstat();o.require(stat.S_ISREG(ns.st_mode)and ns.st_uid==ns.st_gid==0 and stat.S_IMODE(ns.st_mode)==0o600 and ns.st_nlink==1 and ns.st_size>0 and o.sha(native)==whole['nativeSha256'])
files['native.exec']=native.read_bytes()
lower=(root/'run-reservation.safe.json').stat().st_mtime_ns//1000000
o.require(o.tree()==before['tree']and o.database()==before['database']and o.stable_bad()==before['bad']);c.runtime_fixed()
post={'actualExit':0,'source':o.SOURCE,'boot':o.BOOT,'cases':7,'all24AndHistoryTwiceUnchanged':True,'allTenUnitKernelEmpty':True,'clientAdvisoryLockZero':True,'protectedTreeUnchanged':True,'oneFixtureStartAndOwnedStopOnly':True,'oldFailedNativeImported':False,'formalAccepted':False,'nativeLowerMs':lower,'nativeUpperMs':time.time_ns()//1000000+1,'expectedSessionIdSha256':hashlib.sha256(b'PG3222-LFACT-v3').hexdigest(),'nativeSha256':o.sha(native),'beforeSha256':o.sha(root/'before.private.json'),'unitStates':units,'completedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
with(root/'independent-post.safe.json').open('x')as f:json.dump(post,f,sort_keys=True);f.flush();os.fsync(f.fileno())
files['post.safe.json']=(root/'independent-post.safe.json').read_bytes()
capsule={'actualExit':0,'source':o.SOURCE,'boot':o.BOOT,'nativeLowerMs':post['nativeLowerMs'],'nativeUpperMs':post['nativeUpperMs'],'expectedSessionIdSha256':post['expectedSessionIdSha256'],'inputSha256':hashlib.sha256(meta).hexdigest(),'files':{n:hashlib.sha256(v).hexdigest()for n,v in files.items()},'oldFailedNativeImported':False,'formalAccepted':False}
files['capsule.safe.json']=json.dumps(capsule,sort_keys=True).encode()
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|')as tar:
 for name,value in files.items():
  item=tarfile.TarInfo(name);item.size=len(value);item.mode=0o600;item.uid=item.gid=0;tar.addfile(item,io.BytesIO(value))
'''


def main():
    os.umask(0o077); transport.owners()
    proof = json.loads((W / 'pg3224-legacy-negative-v1/execute.safe.json').read_text())
    if proof['actualExit'] != 0: raise ValueError('successful v3 observer terminal required')
    stage = json.loads((W / 'pg3224-legacy-negative-v1/stage.safe.json').read_text())
    raw = 'HASHES=' + repr(stage['hashes']) + '\n' + CODE
    if check(raw, '<complete independent v3 post and capsule>'): raise ValueError('complete post namespace required')
    OUT.mkdir(mode=0o700); (OUT / 'command.private.py').write_text(raw)
    with (OUT / 'capsule.private.tar').open('xb') as log, (OUT / 'stderr.private.log').open('xb') as err:
        result = subprocess.run(transport.ssh() + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), stdout=log, stderr=err, timeout=90)
    if result.returncode: raise ValueError('independent post failed; preserve partial private capsule')
    with tarfile.open(OUT / 'capsule.private.tar', 'r:') as tar:
        members = tar.getmembers(); names = {m.name for m in members}
        if len(names) != len(members) or not all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members): raise ValueError('closed capsule refused')
        manifest = json.loads(tar.extractfile('capsule.safe.json').read())
        if names != set(manifest['files']) | {'capsule.safe.json'}: raise ValueError('exact capsule set required')
        for name, digest in manifest['files'].items():
            if hashlib.sha256(tar.extractfile(name).read()).hexdigest() != digest: raise ValueError('capsule hash refused')
    value = {'actualExit': 0, 'capsuleSha256': hashlib.sha256((OUT / 'capsule.private.tar').read_bytes()).hexdigest(), 'capsule': manifest, 'formalAccepted': False}
    (OUT / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({'actualExit': 0, 'cases': 7, 'all24TwiceTenUnitEmpty': True, 'nativeNotYetQualified': True, 'capsuleSha256': value['capsuleSha256'], 'formalAccepted': False}))


if __name__ == '__main__':
    main()
