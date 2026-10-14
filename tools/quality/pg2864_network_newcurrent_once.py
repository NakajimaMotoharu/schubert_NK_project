"""Full fresh cold-publication proof and durable one noargs Root reservation/start."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg2860_network_cold_publication_post as post
from pg2862_network_newcurrent_observer import namespace,SOURCE,BOM
from pg2852_network_cold_publication_sources import unused
from pg1598_current_ordinary_once import BODY as HISTORICAL

SLOT='pg2864-network-newcurrent-noargs-once-v1'


def observer_body():
    raw=HISTORICAL[:HISTORICAL.index("require(native==after['native']")]
    for a,b in [('pg1597','pg2862'),('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE),
        ('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c',BOM),('PG1544','PG2802')]:raw=raw.replace(a,b)
    old=" for name,digest in WATCH_FILES.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest)"
    new=""" require(metadata(root)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and not os.listxattr(root))
 for name,digest in WATCH_FILES.items():
  p=root/name;m=metadata(p);require(m[2:6]==[0,0,stat.S_IFREG|0o400,1]and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest and m==metadata(p))"""
    return unused.one(raw,old,new).replace("root=base/","root=BASE/")


def payload(hashes):
    raw=post.payload();raw=raw.replace(post.SLOT,SLOT).replace('PG2860-network-cold-publication-independent-post-v1','PG2864-network-newcurrent-noargs-once-v1')
    action='\n'.join(' '+line if line else line for line in observer_body().splitlines())+'\n'+ACTION
    raw=unused.one(raw,'finally:\n errors=[]',action+'finally:\n errors=[]')
    # A started Root now owns resources. Never repeat old post claims of all-zero
    # runtime after dispatch or report old retained-source as currenta9 acceptance.
    begin=raw.index('encoded=json.dumps(')
    raw=raw[:begin]+"print(json.dumps(start_result,sort_keys=True))\nraise SystemExit(r.returncode)\n"
    raw='WATCH_FILES='+repr(hashes)+'\nNEW_SOURCE='+repr(SOURCE)+'\nNEW_BOM='+repr(BOM)+'\n'+raw
    from pyflakes.api import check
    if check(raw,'<whole fresh newboot one ordinary admission>'):raise ValueError('complete once source/observer/finite post graph required')
    compile(raw,'<once external currenta9 ordinary admission>','exec');return raw


ACTION=r'''
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2802'))
 watch=observer()
 declaration=exec_record(first['configuration']['schubert-nk-morning-controller.service']['ExecStart'])
 require(declaration is not None and declaration[1].endswith('dev.codex.schubert.nk.batch.file.MorningProcessMain')and '--resume'not in declaration[1])
 require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active'))
 require(os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize>=12884901888)
 # New cold tmpfs roles are empty: old preserved native is data only, never copied
 # into the new source's runtime qualification or counted as one of its streams.
 for role in ROLE_IDS:require(not os.listdir(ROOT/'pt-coverage'/role))
 def persist(name,value):
  with(SAVE/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
  fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 require(watch==observer()and first==snapshot()and runtime==runtime_check())
 persist('native-before-manifest.private.json',{'newBootRuntimeExecCount':0,'oldPreservedNativeImported':False})
 persist('external-before.private.json',{'immutable':first,'runtime':runtime,'trees':trees,'observer':watch})
 persist('external-start-guard.private.json',{'source':NEW_SOURCE,'manifestSha256':NEW_BOM,'boot':'79a3260a-e16d-42bf-942a-b914ed144c28',
  'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'newRunRequired':True,'originalBudgetSeconds':1800,'attemptReserved':True,'replayAllowed':False,'observer':watch})
 require(watch==observer())
 r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
 manager_state=dict(line.split('=',1)for line in command(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],4096).decode().splitlines())
 start_result=dict(manager_state,clientExit=r.returncode,ordinaryNoargs=True,oldCompletedRunNotResumed=True,newRunRequired=True,
  clientSuccessIsNotParentSuccess=True,originalBudgetSeconds=1800,newBootRuntimeOldNativeImport=False,formalAccepted=False)
 persist('external-start-issued.private.json',start_result)
'''


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed noargs operator required')
    prior=json.loads((W/post.SLOT/'manifest.safe.json').read_bytes());g=prior.get('guest',{})
    if prior.get('actualExit')!=0 or g.get('newCurrentSource')!=SOURCE or g.get('coldPublicationSevenPhasesVerified')is not True:
        raise ValueError('actual newcurrent publication full independent proof required')
    if not(W/'pg2862-watch-v1.started').exists()or(W/'pg2862-watch-v1.exit').exists():raise ValueError('live newsource immutable observer required')
    frames=[json.loads(line)for line in(W/'pg2862-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[v['states']for v in frames if 'states'in v]
    if not states or any(v.get('race')or v['MainPID']!='0'or v['ControlPID']!='0'or v['Job']for v in states[-1].values()):raise ValueError('actual quiescent stable newboot observer frame required')
    hashes={n:hashlib.sha256(raw.encode()).hexdigest()for n,raw in namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg2862-observer-stage-v1').iterdir()}!=hashes:raise ValueError('new immutable observer bytes changed')
    out=W/SLOT;out.mkdir(mode=0o700);raw=payload(hashes).encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        with(out/'observer.private.log').open('xb')as f:r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    value={'actualExit':r.returncode,'operatorSource':head,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw).hexdigest(),
        'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'clientSuccessIsNotParentSuccess':True,'replayForbidden':True}
    if not r.returncode:value['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
