"""SSC211/BUG982 exact retained864 tools only; no business/epoch/current mutation."""
import ast,datetime,hashlib,inspect,json,os,subprocess,sys
from pathlib import Path
from pg866_unused_candidate_post import payload as guard
from pg782_owned_handoff import terminate
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
BODY='''
import signal,select,time
save=pathlib.Path('/var/lib/pgpt-s1-preservation')/('pg868-handoff-'+MODE+'-v1');assert not os.path.lexists(save)
tool=pathlib.Path('/var/lib/pgpt-s1-preservation/pg864-completed-tools-v2');assert {f.name for f in tool.iterdir()}==set(PINS)|{'payload-sha256.json'}
for name,digest in PINS.items():
 p=tool/name;s=p.lstat();assert s.st_uid==s.st_gid==0 and stat.S_ISREG(s.st_mode)and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==digest
assert json.loads((tool/'payload-sha256.json').read_bytes())==PINS
partial=pathlib.Path('/var/lib/pgpt-s1-preservation/pg864-prepare-ro-v1');assert {p.name for p in partial.iterdir()}=={'refs.private.log'}
assert (partial/'refs.private.log').read_bytes()==b'PG864_REF_UNKNOWN type=AssertionError ownershipNotInferred=true\\n'
assert not pathlib.Path('/var/lib/pgpt-s1-preservation/pg864-prepare-ro-v2').exists()
assert not any(line.split()[4]=='/opt/schubert-nk/releases/0.1.0-PG862'for line in pathlib.Path('/proc/self/mountinfo').read_text().splitlines())
def actor(pid,ticks):
 assert (pid,ticks)in ((3585355,18165651),(3585383,18165720))
 p=pathlib.Path('/proc')/str(pid);assert int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks
 argv=(p/'cmdline').read_bytes();wanted='8bf36920f0b1161cbc0785e4795d5e5b5b3bd1ab0bfcbb9a277445fd0a224ea3'if pid==3585355 else'9935394824aab4190e4f119482898ed30d81836cc46e7a1acf5549fda55c2f05'
 assert hashlib.sha256(argv).hexdigest()==wanted
 assert str((p/'exe').readlink())==('/opt/jdk-25.0.4/bin/java'if pid==3585355 else'/usr/bin/python3.14')
 status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l);assert status['Uid'].split()==status['Gid'].split()==['0']*4
 authority={k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid')}
 children={int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}
 if pid==3585355:assert children=={3585383}
 else:assert children==set() and authority['PPid']in ('3585355','1');authority['PPid']='3585355'
 return {'pid':pid,'ticks':ticks,'argvSha256':wanted,'authority':authority,'cgroup':(p/'cgroup').read_text()}
def resources(owned):
 terminal()
 for name in ('maintenance.lock','startup-admission.lock'):
  p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not os.listxattr(p)
  hits=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':')
   if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):hits.append(f)
  assert (len(hits)==1 and hits[0][1:5]==['FLOCK','ADVISORY','WRITE','3585355'])if owned else not hits
 q="select json_build_object('peers',coalesce((select jsonb_agg(jsonb_build_object('pid',pid,'role',usename,'app',application_name)order by pid)from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid<>pg_backend_pid()),'[]'::jsonb),'locks',coalesce((select jsonb_agg(jsonb_build_object('pid',pid,'mode',mode)order by pid)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted),'[]'::jsonb));"
 v=json.loads(subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],text=True))
 if owned:
  assert len(v['peers'])==2 and {r['role']:r['app']for r in v['peers']}=={'schubert_batch':'PG864-fixed-completed','schubert_migration':'PG864-fixed-snapshot'}
  b=next(r['pid']for r in v['peers']if r['role']=='schubert_batch');assert v['locks']==[{'pid':b,'mode':'ExclusiveLock'}]
 else:assert v=={'peers':[],'locks':[]}
 return v
def private(name,value):
 with (save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(value);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def reserve(pid,value):private(str(pid)+'.term-reserved.private.json',json.dumps(value,sort_keys=True).encode())
def wait(fd):
 p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
before=protected();assert before==protected();actors=[actor(3585355,18165651),actor(3585383,18165720)];db=resources(True)
save.mkdir(mode=0o700);private('before.private.json',json.dumps(before,sort_keys=True).encode());private('owners.private.json',json.dumps(actors,sort_keys=True).encode());private('db.private.json',json.dumps(db,sort_keys=True).encode())
if MODE=='execute':
 prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg868-handoff-preflight-v1')
 assert json.loads((prior/'before.private.json').read_bytes())==before and json.loads((prior/'owners.private.json').read_bytes())==actors and json.loads((prior/'db.private.json').read_bytes())==db
 assert before==protected() and resources(True)==db
 terminate(3585355,18165651,actor,reserve,lambda pid:os.pidfd_open(pid,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
 deadline=time.monotonic()+15
 while pathlib.Path('/proc/3585355').exists()and time.monotonic()<deadline:time.sleep(.02)
 assert not pathlib.Path('/proc/3585355').exists()
 if pathlib.Path('/proc/3585383').exists():terminate(3585383,18165720,actor,reserve,lambda pid:os.pidfd_open(pid,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)
 deadline=time.monotonic()+15
 while pathlib.Path('/proc/3585383').exists()and time.monotonic()<deadline:time.sleep(.02)
 assert not pathlib.Path('/proc/3585383').exists();resources(False);assert before==protected()==protected();resources(False)
 private('after.private.json',json.dumps(before,sort_keys=True).encode());private('complete.private',b'oldCloseUnknown=true\\nownedToolsGone=true\\nallResources0=true\\noriginalUnchanged=true\\nstartsStopsRevokePublish0=true\\n')
'''
def payload():
 raw=guard();a=raw.index(" root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')");raw=raw[:a]
 raw=raw.replace('with StageReferences():',inspect.getsource(terminate)+'\nwith StageReferences():')
 raw+=''.join(' '+l+'\n'for l in BODY.splitlines())
 raw+="print(json.dumps({'actualExit':0,'mode':MODE,'allOriginalValuesUnchanged':True,'oldNormalClose':False,'ownedToolsGone':MODE=='execute','allResources0':MODE=='execute','candidateFreezePublishStart0':True}))\n"
 ast.parse(raw);return raw
if __name__=='__main__':
 os.umask(0o077);assert sys.argv[1:]in (['preflight'],['execute']);mode=sys.argv[1]
 assert subprocess.check_output(['git','status','--porcelain'])==b''
 frozen=json.loads((W/'pg864-frozen-v2.safe.json').read_bytes());assert frozen['actualExit']==0
 prefix='MODE='+repr(mode)+'\nPINS='+repr(frozen['fileHashes'])+'\n'
 raw=prefix+payload();base=W/('pg868-handoff-'+mode+'-v1');assert not Path(str(base)+'.safe.json').exists()and not Path(str(base)+'.private.log').exists()
 if mode=='execute':assert json.loads((W/'pg868-handoff-preflight-v1.safe.json').read_bytes())['actualExit']==0
 start=datetime.datetime.now(datetime.timezone.utc)
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 with Path(str(base)+'.private.log').open('xb')as f:r=subprocess.run(ssh,input=raw.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
 safe={'run':'PG868-handoff-'+mode+'-v1','actualExit':r.returncode,'mode':mode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'payloadSha256':hashlib.sha256(payload().encode()).hexdigest(),'oldNormalClose':False,'formalAccepted':False}
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.flush();os.fsync(f.fileno())
 print(json.dumps(safe));raise SystemExit(r.returncode)
