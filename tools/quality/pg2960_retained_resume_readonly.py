"""SSC276 failed-phase single queued recovery operator, read-only proof/no signals."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1724_retained_host_gate import queued_gate

SLOT='pg2960-retained-resume-readonly-v1'


def host_owner(path):
    p=Path('/proc/77110');s=(p/'stat').read_text().rsplit(')',1)[1].split()
    if int(s[19])!=1738713 or int(s[1])!=4249 or hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()!='f84e090d6bc59d98c4573aa768fc100b25812be80d6b164cc18812f463d7d971':raise ValueError('exact retained wrapper only')
    g=path.stat();f=(p/'fd/4').stat()
    if(g.st_dev,g.st_ino)!=(66306,9337730)or(g.st_dev,g.st_ino)!=(f.st_dev,f.st_ino):raise ValueError('same existing gate inode required')
    owners=[]
    for line in Path('/proc/locks').read_text().splitlines():
        v=line.split()
        if len(v)>=8 and v[1]=='FLOCK'and v[5]=='103:02:9337730':owners.append(v[1:5])
    if owners!=[['FLOCK','ADVISORY','WRITE','77110']]:raise ValueError('sole unchanged host exclusion required')


BODY=r'''
import hashlib,json,os,pathlib,re,subprocess
os.umask(0o077)
def require(v):
 if not v:raise ValueError('retained read-only proof refused')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg2960-retained-resume-readonly-v1'
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'and not os.path.lexists(save))
require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2802'))
actors=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  argv=(p/'cmdline').read_bytes();exe=str((p/'exe').readlink())
 except (OSError,ValueError):continue
 if not exe.endswith('/java')or b'Pg2950FreshResumePreparation'not in argv:continue
 fields=(p/'stat').read_text().rsplit(')',1)[1].split();status=(p/'status').read_text();fds={}
 require(re.search(r'^Uid:\s+0\s+0\s+0\s+0$',status,re.M)and re.search(r'^Gid:\s+0\s+0\s+0\s+0$',status,re.M))
 for f in (p/'fd').iterdir():
  try:
   target=os.readlink(f);s=f.stat();fds[f.name]={'target':target,'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'fdinfo':(p/'fdinfo'/f.name).read_text()}
  except FileNotFoundError:require(False)
 children=set()
 for task in (p/'task').iterdir():children.update(int(n)for n in (task/'children').read_text().split())
 actors.append({'pid':int(p.name),'ppid':int(fields[1]),'ticks':int(fields[19]),'argvSha256':hashlib.sha256(argv).hexdigest(),'argv':argv.decode().split(chr(0)),'exe':exe,'status':status,'root':os.readlink(p/'root'),'cgroup':(p/'cgroup').read_text(),'fds':fds,'children':sorted(children)})
require(len(actors)==1)
root=pathlib.Path('/run/systemd/system');runtime={str(p):[p.lstat().st_mode,p.lstat().st_uid,p.lstat().st_gid,p.lstat().st_ino]for p in [root,*root.rglob('*')]}
work=base/'pg2954-current-cold-resume-preparation-v1';entries=sorted(p.name for p in work.iterdir());log=(work/'refs-prepare.private.log').read_bytes()
q="begin read only;select json_build_object('pid',pid,'role',usename,'application',application_name,'state',state,'backendStart',backend_start,'address',client_addr,'port',client_port)from pg_stat_activity where datname='schubert_nk'and pid<>pg_backend_pid();select json_build_object('pid',pid,'mode',mode,'granted',granted)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1;commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=q.encode(),capture_output=True,timeout=15);require(r.returncode==0)
locks=[]
for name in ['maintenance.lock','startup-admission.lock']:
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}'
 locks.append({'name':name,'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'locks':[l for l in pathlib.Path('/proc/locks').read_text().splitlines()if key in l]})
value={'actors':actors,'runtime':runtime,'privateEntries':entries,'failureLogSha256':hashlib.sha256(log).hexdigest(),'peerRows':r.stdout.decode().splitlines(),'locks':locks,'signals0':True,'writesBusiness0':True,'oldUnknown':True}
save.mkdir(mode=0o700)
for name,data in [('proof.private.json',json.dumps(value,sort_keys=True).encode()),('refs-failure.private.log',log)]:
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
for p in [save,base]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
frames=[l for l in log.decode().splitlines()if re.match(r'\s*File ".*", line [0-9]+',l)]
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256((save/'proof.private.json').read_bytes()).hexdigest(),'actor':{k:actors[0][k]for k in ['pid','ppid','ticks','argvSha256','children']},'actorFdCount':len(actors[0]['fds']),'runtimeEntryCount':len(runtime),'privateEntries':entries,'failureFrames':frames,'failureLogSha256':value['failureLogSha256'],'peerRowCount':len(value['peerRows']),'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(BODY)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with queued_gate(P/'current-management-critical.lock',validate_owner=host_owner,require_completion=lambda:False):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=BODY.encode(),capture_output=True,timeout=60)
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'result.private.json').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(BODY.encode()).hexdigest(),'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'signals0':True,'oldHostOwnerRetained':True,'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
