"""Readonly fixed currently retained779 ownership/42 namespace/full24. No replay or stop."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import sys,pathlib,json,os,hashlib,stat,subprocess
os.umask(0o077);assert os.geteuid()==0
tools=pathlib.Path('/var/lib/pgpt-s1-preservation/pg779-failed758-tools-v1')
files=json.loads((tools/'payload-sha256.json').read_text())
for n,d in files.items():assert hashlib.sha256((tools/n).read_bytes()).hexdigest()==d
sys.path.insert(0,str(tools));import pg779_owned as h
h.load_definitions();h.parent()
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg780-retained779-current-v1');assert not os.path.lexists(save)
def actor(pid,ticks,kind):
 p=pathlib.Path('/proc')/str(pid);s=(p/'stat').read_text();assert s[s.rindex(')')+2:].split()[19]==str(ticks)
 argv=(p/'cmdline').read_bytes();status=(p/'status').read_text();fds={}
 assert (b'Pg779FailedRecovery\0recover\0'in argv if kind=='java'else b'/pg779_refs.py\0recover\0'in argv)
 for f in (p/'fd').iterdir():
  try:fds[f.name]=str(f.readlink())
  except FileNotFoundError:continue
 return {'pid':pid,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),'status':status,'cgroup':(p/'cgroup').read_text(),'exe':str((p/'exe').readlink()),'fds':fds}
a=actor(3105271,14283385,'java');b=actor(3105303,14283477,'refs')
assert a['exe']=='/opt/jdk-25.0.4/bin/java'
for name in ('maintenance.lock','startup-admission.lock'):
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();assert str(p)in a['fds'].values()and stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==s.st_gid==0
 found=[]
 for row in pathlib.Path('/proc/locks').read_text().splitlines():
  f=row.split()
  if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE','3105271']:
   d=f[5].split(':')
   if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):found.append(row)
 assert len(found)==1
db=subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"select jsonb_agg(jsonb_build_object('pid',a.pid,'application',a.application_name,'username',a.usename,'advisory',exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.granted)))from pg_stat_activity a where a.application_name in ('PG779-fixed-recovery','PG779-fixed-snapshot');"])
sessions=json.loads(db);assert len(sessions)==2 and sum(x['advisory']for x in sessions)==1
before=h.snapshot();assert before==h.snapshot()
unit_values={u:h.show(u)for u in h.ORDER+h.EXTRA}
for u,v in unit_values.items():assert v['MainPID']==v['ControlPID']=='0'and not v['Job'];h.kernel_empty(u)
startup=pathlib.Path('/run/schubert-nk/startup');names={p.name for p in startup.iterdir()}
assert len(names)==42 and {n for n in names if n.endswith('.intent')}=={'permit-start.intent','e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent','e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent'}
assert h.epoch_value((startup/'epoch.current').read_bytes(),True)
startup_bytes={p.name:p.read_bytes().hex()for p in startup.iterdir()};assert a==actor(3105271,14283385,'java')and b==actor(3105303,14283477,'refs')
value={'source':'8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','owner':a,'refs':b,'sessions':sessions,'units':unit_values,'snapshot':before,'startupBytes':startup_bytes,'oldReceiptTree':h.tree(h.ROOT),'toolFiles':files}
save.mkdir(mode=0o700)
with(save/'current.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for d in(save,save.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'readonly':True,'javaPid':3105271,'javaTicks':14283385,'refsPid':3105303,'refsTicks':14283477,'allTenKernel0':True,'all24RowsPreserved':True,'batchRows':544,'startupEntries':42,'threeIntentsHeld':True,'sameEpochInvalid':True,'old779NormalReturn':False,'startsStopsRevoke0':True,'snapshotSha256':hashlib.sha256((save/'current.private.json').read_bytes()).hexdigest()}))
'''


def main():
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'])
    base=W/'pg780-retained779-current-v1';assert not any(Path(str(base)+s).exists()for s in ('.exit','.safe.json','.private.stderr'))
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    with Path(str(base)+'.private.stderr').open('xb')as f:r=subprocess.run(ssh,input=PAYLOAD.encode(),stdout=subprocess.PIPE,stderr=f,timeout=90)
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    if r.returncode==0:
        value=json.loads(r.stdout);value.update(recordedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
        print(json.dumps(value))
    else:print(json.dumps({'actualExit':r.returncode,'privateErrorSha256':hashlib.sha256(Path(str(base)+'.private.stderr').read_bytes()).hexdigest()}))
    raise SystemExit(r.returncode)


if __name__=='__main__':main()
