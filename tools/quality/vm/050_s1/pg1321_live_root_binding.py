"""Fresh live Root identity/original binding; readonly, no permit/credential export."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1257_fresh_independent_terminal_post import W,SSH
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST

BODY=r'''
import datetime,hashlib,json,os,pathlib,stat,subprocess,time,uuid
def require(v):
 if not v:raise ValueError('live newsource Root binding refused')
def meta(s):return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def show():
 raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=MainPID,ControlPID,Job,InvocationID,ExecMainStartTimestampMonotonic,ActiveState,SubState'],text=True,timeout=5)
 return dict(line.split('=',1)for line in raw.splitlines())
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6')
release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1292'and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()==DIGEST)
unit=show();require(unit['MainPID']==EXPECTED['MainPID']and unit['InvocationID']==EXPECTED['InvocationID']and unit['ExecMainStartTimestampMonotonic']==EXPECTED['ExecMainStartTimestampMonotonic']and unit['ActiveState']=='activating'and unit['SubState']=='start'and unit['Job']==EXPECTED['Job'])
p=pathlib.Path('/proc')/unit['MainPID'];argv=(p/'cmdline').read_bytes();status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
require(argv.endswith(b'dev.codex.schubert.nk.batch.file.MorningProcessMain\0')and status['Uid'].split()==status['Gid'].split()==['0']*4)
ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19]);require(ticks==int(unit['ExecMainStartTimestampMonotonic'])//10000)
active=pathlib.Path('/var/lib/schubert-nk/maintenance/active');m=meta(active.lstat());require(stat.S_ISREG(m[4])and(m[2],m[3],stat.S_IMODE(m[4]),m[5])==(0,0,0o600,1)and 0<m[6]<=512 and not os.listxattr(active))
raw=active.read_bytes();fields=raw.decode('ascii').splitlines();require(raw.endswith(b'\n')and len(fields)==4 and fields[0]=='NKACT1')
for v in [fields[1],fields[3]]:
 u=uuid.UUID(v);require(str(u)==v and u.version==4 and u.variant==uuid.RFC_4122)
cut=datetime.datetime.fromisoformat(fields[2].replace('Z','+00:00'));require(fields[2].endswith('Z')and cut.tzinfo is not None)
for name,expected in [('runs/'+fields[1]+'.run',('NKRUN1\n'+fields[1]+'\n'+fields[2]+'\n').encode()),('attempts/'+fields[3]+'.begin',raw)]:
 a=active.parent/name;s=a.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(a)and a.read_bytes()==expected)
require(meta(active.lstat())==m and active.read_bytes()==raw and show()==unit and(p/'cmdline').read_bytes()==argv and int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks)
print(json.dumps({'binding':{'boot':'cbca87383b244090b77cbf029677cdd6','invocation':unit['InvocationID'],'job':unit['Job'],'start':int(unit['ExecMainStartTimestampMonotonic']),'run':fields[1],'cutoff':fields[2],'activation':fields[3]},'rootPid':int(unit['MainPID']),'rootTicks':ticks,'rootArgvSha256':hashlib.sha256(argv).hexdigest(),'activeSha256':hashlib.sha256(raw).hexdigest(),'productionSource':SOURCE,'originalBudgetSeconds':1800,'startsStops0':True,'rawExported':False,'formalAccepted':False}))
'''


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean current tools required')
    start=json.loads((W/'pg1320-published-ordinary-once-v1.safe.json').read_bytes())
    if start['actualExit']!=0 or start['productionSource']!=SOURCE or not start['externalStartIssuedOnce']:raise ValueError('actual once start required')
    code='SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\nEXPECTED='+repr(start['parent'])+'\n'+BODY
    compile(code,'<actual live original binding>','exec')
    base=W/'pg1321-live-root-binding-v1'
    if any(Path(str(base)+s).exists()for s in ['.safe.json','.private.log','.exit']):raise ValueError('new-only identity capture required')
    began=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(SSH,input=code.encode(),capture_output=True,timeout=30)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    v={'actualExit':r.returncode,'startedUTC':began,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'logSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:v.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
