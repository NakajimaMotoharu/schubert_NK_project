"""One current758 failure snapshot/journal, readonly business; private bytes neverstdout."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import ast,hashlib,json,os,pathlib,subprocess,time
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg771-failure-current758-v1';assert not os.path.lexists(save)
source='8d4b68b4f1449932ebe506aaf08e584bbfea8dd2';digest='a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'
release=pathlib.Path('/opt/schubert-nk/current');raw=(release/'RELEASE-MANIFEST.json').read_bytes()
assert release.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG750')and hashlib.sha256(raw).hexdigest()==digest and json.loads(raw)['source']['commit']==source
helper=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();assert hashlib.sha256(helper).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
nodes=[n for n in ast.parse(helper).body if isinstance(n,ast.FunctionDef)and n.name in ('command','metadata','tree')];assert len(nodes)==3;exec(compile(ast.Module(body=nodes,type_ignores=[]),'<sealedreadonly>','exec'),globals())
units=('schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service','artemis.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','schubert-nk-bootstrap-admin.service')
fields='Id,LoadState,ActiveState,SubState,MainPID,ControlPID,InvocationID,Job,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,TimeoutStartUSec,TimeoutStopUSec,KillMode,SendSIGKILL'
def actors():
 out={}
 for u in units:
  d=dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show',u,'--property='+fields],text=True).splitlines());d['kernelPids']=[]
  cg=pathlib.Path('/sys/fs/cgroup/system.slice')/u
  for file in cg.glob('**/cgroup.procs'):d['kernelPids'].extend(file.read_text().split())
  if d['MainPID']!='0':
   p=pathlib.Path('/proc')/d['MainPID'];data=p.joinpath('cmdline').read_bytes();stat=p.joinpath('stat').read_text()
   d['actor']={'ticks':stat[stat.rindex(')')+2:].split()[19],'argvSha256':hashlib.sha256(data).hexdigest(),'exe':str(p.joinpath('exe').readlink())}
  out[u]=d
 return out
a=actors();parent=a[units[0]]
assert parent['InvocationID']=='e4093109ab234700b61dd45711126e4e'and parent['ExecMainStartTimestampMonotonic']=='137240785885'and parent['MainPID']==parent['ControlPID']=='0'and not parent['Job']and parent['Result']=='timeout'and parent['ExecMainStatus']=='143'
assert not pathlib.Path('/proc/2797579').exists()
epoch=dict(l.split('=',1)for l in pathlib.Path('/run/schubert-nk/startup/epoch.current').read_text().splitlines()[1:])
assert epoch['run_id']=='9de2d03c-28c7-4647-97d9-c66ace06048c'and epoch['cutoff_utc']=='2026-10-09T05:42:22.532331Z'and epoch['activation_id']=='021111b4-6de5-4733-917d-5ac176240ffc'
journal=command(['journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_SYSTEMD_INVOCATION_ID='+parent['InvocationID'],'-o','json','--no-pager'],16777216)
pid1=command(['journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT='+units[0],'INVOCATION_ID='+parent['InvocationID'],'-o','json','--no-pager'],16777216)
trees={n:tree(pathlib.Path(path))for n,path in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('native','/run/schubert-nk/pt-coverage')]}
b=actors();assert all(a[u]['MainPID']==b[u]['MainPID']and a[u]['InvocationID']==b[u]['InvocationID']and a[u]['Job']==b[u]['Job']for u in units)
save.mkdir(mode=0o700)
for name,raw in {'snapshot.private.json':json.dumps({'source':source,'manifestSha256':digest,'beforeActors':a,'afterActors':b,'epochFields':{k:epoch[k]for k in ('state','boot_id','epoch_id','run_id','cutoff_utc','activation_id')},**trees},sort_keys=True).encode(),'journal.private.jsonl':journal,'pid1.private.jsonl':pid1}.items():
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
for d in (save,save.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
done=pathlib.Path('/run/schubert-nk/startup')/(epoch['activation_id']+'.done')
print(json.dumps({'actualExit':0,'diagnosticOnly':True,'source':source,'parentResult':'timeout','parentExit':143,'parentStartMonotonicUs':int(parent['ExecMainStartTimestampMonotonic']),'parentEndMonotonicUs':int(parent['ExecMainExitTimestampMonotonic']),
 'currentActors':{u:{k:v[k]for k in ('MainPID','InvocationID','ActiveState','SubState','Job')}for u,v in b.items()},'rootDoneFileExists':done.exists(),'nativeFiles':sum(v['sha256']is not None for v in trees['native'].values()),
 'originalActive':os.path.lexists('/var/lib/schubert-nk/maintenance/active'),'originalPending':os.path.lexists('/var/lib/schubert-nk/maintenance/pending'),
 'snapshotSha256':hashlib.sha256((save/'snapshot.private.json').read_bytes()).hexdigest(),'journalSha256':hashlib.sha256(journal).hexdigest(),'pid1Sha256':hashlib.sha256(pid1).hexdigest(),
 'startsStopsWrites0':True,'genuineDoneAccepted':False,'oldUnknownNormalized':False}))
'''


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])
    base=W/'pg771-failure-current758-v1'
    assert not any(Path(str(base)+'.'+s).exists()for s in ('private.stderr','safe.json','exit'))
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    with Path(str(base)+'.private.stderr').open('xb')as f:
        result=subprocess.run(ssh,input=PAYLOAD.encode(),stdout=subprocess.PIPE,stderr=f,timeout=90);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout);safe.update(recordedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip())
        with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        print(json.dumps(safe))
    else:print(json.dumps({'actualExit':result.returncode,'privateStderrSha256':hashlib.sha256(Path(str(base)+'.private.stderr').read_bytes()).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
