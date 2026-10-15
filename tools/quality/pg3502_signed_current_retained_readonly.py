"""SSC276 frozen SIGNED_CURRENT failed-phase single diagnostic; no Ref/lease/signal.

The existing wrapper keeps the exclusive gate. This one queued recovery operator
uses the already approved failed-phase read-only exception, never force-unlocks.
Raw FD/DB material is private; stdout contains only metadata/counts and hashes.
"""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate

SLOT = 'pg3502-signed-current-retained-readonly-v1'
LOG_SHA = '197a2ae89c6bff74e9e38753e807a2e89b85ae9da0a5f10a512a2107c3817281'


def host_owner(path):
    p = Path('/proc/347505')
    s = (p / 'stat').read_text().rsplit(')', 1)[1].split()
    raw = (p / 'cmdline').read_bytes()
    if (int(s[19]) != 8560863 or int(s[1]) != 4249
            or hashlib.sha256(raw).hexdigest() != '6db8bae1dc1b431ebfb40258f9ff0ba03543150ba8e60acf2ec0917eed9cb47d'):
        raise ValueError('exact existing failed wrapper required')
    linked = path.stat()
    fd = (p / 'fd/4').stat()
    if (linked.st_dev, linked.st_ino) != (66306, 9337730) or (fd.st_dev, fd.st_ino) != (linked.st_dev, linked.st_ino):
        raise ValueError('same sole host gate descriptor required')
    key = f'{os.major(linked.st_dev):02x}:{os.minor(linked.st_dev):02x}:{linked.st_ino}'
    owners = [line.split()[1:5] for line in Path('/proc/locks').read_text().splitlines()
              if len(line.split()) >= 8 and line.split()[1] == 'FLOCK' and line.split()[5] == key]
    failure = (W / 'pg3494-stop-v1.private.log').read_bytes()
    if (owners != [['FLOCK', 'ADVISORY', 'WRITE', '347505']]
            or hashlib.sha256(failure).hexdigest() != LOG_SHA
            or b'PG3490_RUNTIME_RESUME_UNKNOWN phase=SIGNED_CURRENT type=java.io.IOException ' not in failure
            or (W / 'pg3494-stop-v1.exit').exists()):
        raise ValueError('same frozen failed phase, no terminal or second operator')


def payload():
    path = W / 'pg3476-outbox-current-full-seal-v1/payload.private.py'
    proof = json.loads((path.parent / 'manifest.safe.json').read_bytes())
    raw = path.read_text()
    if proof['actualExit'] != 0 or hashlib.sha256(raw.encode()).hexdigest() != proof['payloadSha256']:
        raise ValueError('actual full seal metadata reader required')
    functions = [ast.get_source_segment(raw, n) for n in ast.parse(raw).body
                 if isinstance(n, ast.FunctionDef) and n.name in ['metadata', 'tree']]
    if len(functions) != 2:
        raise ValueError('two exact source metadata readers required')
    return '\n'.join(functions) + '\n' + BODY


BODY = r'''
import hashlib,json,os,pathlib,stat,subprocess,datetime
os.umask(0o077)
def require(v):
 if not v:raise ValueError('current SIGNED_CURRENT failed-phase read-only proof refused')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg3502-signed-current-retained-readonly-v1'
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'and not os.path.lexists(save))
require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG3420'))
seal_raw=(base/'pg3476-outbox-current-full-seal-v1/before.private.json').read_bytes();require(hashlib.sha256(seal_raw).hexdigest()=='84a90ccb784eddfe027ce5045fb0f5230777f0e25f0ad314ced3fc38a8dcc462')
seal=json.loads(seal_raw)
def actors():
 result=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdecimal():continue
  try:argv=(p/'cmdline').read_bytes();exe=str((p/'exe').readlink())
  except(FileNotFoundError,ProcessLookupError,PermissionError):continue
  if not exe.endswith('/java')or b'Pg3490NativeStop\x00stop\x00'not in argv:continue
  st=(p/'stat').read_text().rsplit(')',1)[1].split();status=(p/'status').read_text();fields=dict(x.split(':',1)for x in status.splitlines()if ':'in x)
  require(fields['Uid'].split()==fields['Gid'].split()==['0']*4)
  fds={}
  for f in (p/'fd').iterdir():
   s=f.stat();fds[f.name]={'target':os.readlink(f),'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'fdinfo':(p/'fdinfo'/f.name).read_text()}
  children=set()
  for task in(p/'task').iterdir():children.update(int(n)for n in(task/'children').read_text().split())
  result.append({'pid':int(p.name),'ppid':int(st[1]),'ticks':int(st[19]),'argvSha256':hashlib.sha256(argv).hexdigest(),'argv':argv.decode().split(chr(0)),'exe':exe,'status':status,'root':os.readlink(p/'root'),'cgroup':(p/'cgroup').read_text(),'fds':fds,'children':sorted(children)})
 require(len(result)==1);return result
a=actors();require(not a[0]['children'])
require(not os.path.lexists(base/'pg3490-native-stop-v1'))
units={}
for name,old in seal['units'].items():
 r=subprocess.run(['systemctl','show',name,'--property='+','.join(sorted(old))],capture_output=True,text=True,timeout=5);require(r.returncode==0)
 units[name]=dict(x.split('=',1)for x in r.stdout.splitlines())
for name,old in seal['actors'].items():
 p=pathlib.Path('/proc')/seal['units'][name]['MainPID'];st=(p/'stat').read_text().rsplit(')',1)[1].split()
 require(int(st[19])==old['ticks']and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==old['argvSha256']and(p/'cgroup').read_text()==old['cgroup'])
sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';"
for t in seal['rows']:
 require(t.startswith('schubert.')or t.startswith('schubert_web_session.'))
 sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+' t)q;'
sql+="select json_build_object('peer',json_build_object('pid',pid,'role',usename,'application',application_name,'state',state,'backendStart',backend_start,'address',client_addr,'port',client_port))from pg_stat_activity where datname='schubert_nk'and pid<>pg_backend_pid();select json_build_object('advisory',json_build_object('pid',pid,'granted',granted))from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1;commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],capture_output=True,timeout=30);require(r.returncode==0 and len(r.stdout)<67108864)
rows={};peers=[];advisory=[]
for line in r.stdout.splitlines():
 v=json.loads(line)
 if'table'in v:require(v['table']not in rows);rows[v['table']]=v['rows']
 elif'peer'in v:peers.append(v['peer'])
 else:require('advisory'in v);advisory.append(v['advisory'])
require(len(rows)==24 and rows==seal['rows'])
require(not any(p['application']=='PG998-native-stop'for p in peers)and not advisory)
locks=[]
for name in ['maintenance.lock','startup-admission.lock']:
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}'
 locks.append({'name':name,'metadata':metadata(p),'locks':[l for l in pathlib.Path('/proc/locks').read_text().splitlines()if len(l.split())>=8 and l.split()[5]==key]})
durable={k:tree(pathlib.Path(os.path.commonpath(list(v))))for k,v in seal['durable'].items()};require(durable==seal['durable'])
native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'));require(native==seal['native'])
runtime=tree(pathlib.Path('/run/systemd/system'));require(runtime==seal['runtime'])
startup=tree(pathlib.Path('/run/schubert-nk/startup'));require(startup==seal['startup'])
release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG3420');manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()=='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72')
for v in json.loads(manifest)['artifacts']:
 p=release/v['path'];s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and s.st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
b=actors();require(a==b)
value={'actors':a,'units':units,'rows':rows,'peers':peers,'advisory':advisory,'locks':locks,'durable':durable,'native':native,'runtime':runtime,'startup':startup,'signals0':True,'businessWrites0':True,'oldUnknown':True}
save.mkdir(mode=0o700);encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,base]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'proofSha256':hashlib.sha256(encoded).hexdigest(),'actor':{k:a[0][k]for k in ['pid','ppid','ticks','argvSha256','children']},'actorFdCount':len(a[0]['fds']),'all24Unchanged':True,'fourOrdinaryOwnersUnchanged':True,'all187ArtifactBytesUnchanged':True,'originalBackupNativeRuntimeStartupUnchanged':True,'managementDbAbsent':True,'advisory0':True,'managementLockCounts':[len(v['locks'])for v in locks],'failureSaveDirectoryAbsent':True,'signals0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077)
    out = W / SLOT
    out.mkdir()
    raw = payload()
    if check(raw, '<complete frozen-phase read-only diagnostic>'):
        raise ValueError('whole diagnostic exports required')
    (out / 'payload.private.py').write_text(raw)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with queued_gate(P / 'current-management-critical.lock', validate_owner=host_owner, require_completion=lambda: False):
        result = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=150)
        host_owner(P / 'current-management-critical.lock')
    (out / 'stderr.private.log').write_bytes(result.stderr)
    (out / 'stdout.private.json').write_bytes(result.stdout)
    value = {'actualExit': result.returncode, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),
             'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'hostGateRetainedUnchanged': True, 'forceUnlock': False, 'formalAccepted': False}
    if result.returncode == 0:
        value['guest'] = json.loads(result.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
