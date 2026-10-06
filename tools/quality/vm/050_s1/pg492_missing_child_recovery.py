"""SSC202/BUG797 exact missing-child owned TERM; never normal scope closure."""
import ast,hashlib,json,os,pathlib,signal,stat,subprocess,time
assert os.geteuid()==0
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54';PID=3901807;TICKS=25468538
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg492-missing-child-recovery')
assert not SAVE.exists();os.umask(0o077)
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg491-pending-codeonly/refs-after.private.json').read_bytes()
assert hashlib.sha256(base).hexdigest()=='e22a7bc163dc873bf01c0e8163bc664ccf3c81b3ed430f19d7f9dca1bc413a01'
previous=json.loads(base)
UNITS=list(previous['units'])
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
names={'require','command','show','metadata','tree','kernel'}
defs=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==len(names)
exec(compile(ast.Module(body=defs,type_ignores=[]),'<immutable readback>','exec'),globals())
def owner():
 p=pathlib.Path('/proc')/str(PID)
 assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
 assert int((p/'stat').read_text().rpartition(')')[2].split()[19])==TICKS
 assert (p/'cmdline').read_bytes().split(b'\0')[-4:]==[b'Pg492ResumePreparation',b'38899a05b5c2daeecfc5af8ea5ae748e29954c60',b'652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c',b'']
 assert (p/'status').read_text().split('Uid:\t')[1].splitlines()[0].split()==['0']*4
 assert pathlib.Path('/proc/'+str(PID)+'/task/'+str(PID)+'/children').read_text().strip()==''
 held={str(fd.readlink()) for fd in (p/'fd').iterdir()}
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;assert str(path) in held
  s=path.stat();matches=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matches.append(line)
  assert len(matches)==1
def database(expect_owned):
 sql="select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_backup','schubert_inbox_inspector','schubert_web_session'); select count(*) from pg_stat_activity a join pg_locks l on l.pid=a.pid where a.datname='schubert_nk' and a.usename='schubert_batch' and a.application_name='PG492-fixed-resume' and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted; select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"
 v=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql],4096).splitlines()
 # The readonly operator DB can expire under its pre-existing idle TX timeout;
 # absence is not a normal close and never authorizes a foreign peer.
 assert v in ([ [b'1',b'1',b'1'], [b'0',b'0',b'0'] ] if expect_owned else [[b'0',b'0',b'0']])
def unchanged():
 assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
 assert str(pathlib.Path('/opt/schubert-nk/current').readlink())==previous['current']
 for u in previous['units']:
  assert show(u,set(previous['units'][u]))==previous['units'][u];kernel(u)
  assert show(u,set(previous['configuration'][u]))==previous['configuration'][u]
 for root,values in previous['trees'].items():assert tree(pathlib.Path(root))==values
 assert not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir())
 assert not pathlib.Path('/var/lib/pgpt-s1-preservation/pg492-resume-preparation').exists()
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for table in previous['rows']:q+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 q+='commit;'
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines():
  v=json.loads(line);assert v['table'] not in rows;rows[v['table']]=v['rows']
 assert rows==previous['rows']
owner();database(True);unchanged()
assert pathlib.Path('/var/lib/pgpt-s1-preservation/pg492-resume-tools-v1/refs-prepare.private.log').read_bytes()==b"/usr/bin/python3: can't open file '/var/lib/pgpt-s1-preservation/pg492-resume-tools-v1/pg481_resume_refs.py': [Errno 2] No such file or directory\n"
SAVE.mkdir(mode=0o700)
def save(name,value):
 with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
save('owned-term-reservation.private.json',{'pid':PID,'ticks':TICKS,'boot':BOOT,'attemptReserved':True,'repeatForbidden':True,'normalClosure':False})
owner();os.kill(PID,signal.SIGTERM)
deadline=time.monotonic()+15
while pathlib.Path('/proc/'+str(PID)).exists() and time.monotonic()<deadline:time.sleep(.05)
assert not pathlib.Path('/proc/'+str(PID)).exists()
database(False);unchanged();database(False);unchanged()
save('complete.private.json',{'ownedTerm':True,'allOriginalValuesUnchanged':True,'businessPeers0':True,'advisory0':True,'runtimeFiles0':True,'normalScopeClosure':False,'oldCloseNotInferred':True})
print('PG492_MISSING_CHILD_RECOVERED ownedTerm=true unchanged=true newOldNormalClosure=false starts0=true')
