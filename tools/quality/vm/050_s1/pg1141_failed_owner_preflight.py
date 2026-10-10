"""SSC257 read-only current terminal/originals and fixed UNKNOWN owner proof.

No service/epoch/DB mutation or signal. Previous stop is never replayed.
Private raw remains guest Root only; output is safe proof metadata.
"""
import ast
import inspect
import json
from pg1132_current_failed_capture_v6 import payload as previous
from pg870_ordinary_before import parser_source
from pg1041_cold_policy_diagnostic import W
import pg1133_fixed_broker_policy as broker_policy
import pg1140_dependent_oneshot_policy as dependent
import pg1120_current_failed_capture as transport

BASE = '/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/failed-capture-v6/observed.private.json'
SHA = 'df0b989893adbddd6a539b963c07029222c47e1b557cd572f44fdb8864f1fb01'


def payload():
    frozen = json.loads((W / 'pg1138-failed-recovery-frozen-v3.safe.json').read_bytes())
    if frozen['actualExit'] != 0: raise ValueError('fixed qualified old tool input refused')
    raw = previous().replace('failed-capture-v6', 'failed-owner-preflight-v1')
    # Keep the original archive's fixed path, never substitute the new save destination.
    extra = "\nraw_failure=pathlib.Path(" + repr(BASE) + ").read_bytes()\nrequire(hashlib.sha256(raw_failure).hexdigest()==" + repr(SHA) + ")\nFAILED=json.loads(raw_failure)\n"
    marker = 'def capture():\n'
    if raw.count(marker) != 1: raise ValueError('fixed current ownership capture insertion refused')
    raw = raw.replace(marker, extra + marker)
    start = raw.index(" live={u:v for u,v in us.items()")
    end = raw.index(' for u in units:\n', start)
    raw = raw[:start] + ''' deps=show('schubert-nk-expiry-cleanup.service',{'Requires','BindsTo','PartOf'})
 dependent.whole(FAILED['units'],us,deps,cleanup_active=True)
 actor=FAILED['actor']
 require(not pathlib.Path('/proc/253968').exists())
''' + raw[end:]
    raw = raw.replace("if u!='artemis.service':kernel(u)", 'kernel(u)')
    marker = ' resource_zero()\n return'
    if raw.count(marker) != 1: raise ValueError('fixed terminal configuration join refused')
    raw = raw.replace(marker, ''' configuration={u:show(u,configuration_fields())for u in units}
 for u in units:
  if u=='artemis.service':broker_policy.configuration(FAILED['configuration'][u],configuration[u],FAILED['units'][u],us[u],exec_record)
  else:require(configuration[u]==FAILED['configuration'][u])
 resource_zero()
 return''')
    raw = raw.replace("'configuration':{u:show(u,configuration_fields())for u in units}", "'configuration':configuration")
    end = raw.index('bus=dbus.SystemBus(private=True);manager=dbus.Interface')
    raw = raw[:end] + BODY
    raw = "import types,sys\nbroker_policy=types.ModuleType('broker-policy')\nexec(" + repr(inspect.getsource(broker_policy)) + ",broker_policy.__dict__)\nsys.modules['pg1133_fixed_broker_policy']=broker_policy\ndependent=types.ModuleType('dependent-policy')\nexec(" + repr(inspect.getsource(dependent)) + ",dependent.__dict__)\n" + parser_source() + raw
    raw = 'FILES=' + repr(frozen['fileHashes']) + '\n' + raw
    ast.parse(raw); return raw


BODY = r'''
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def actor_proof(pid,ticks,digest,exe,child):
 p=pathlib.Path('/proc')/str(pid)
 require(tick(pid)==ticks and str((p/'exe').readlink())==exe and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==digest)
 require((p/'status').read_text().split('Uid:')[1].splitlines()[0].split()==['0']*4)
 children={int(v)for t in (p/'task').iterdir()for v in (t/'children').read_text().split()}
 require(children==child)
 require(tick(pid)==ticks and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==digest)
 return {'pid':pid,'ticks':ticks,'argvSha256':digest,'children':sorted(children),'exe':exe}
def owner():
 java=actor_proof(404585,4248646,'61d39d9b14028d6861a43af6b68502107d5b30a8c5c7ec8eeedd2e715f6d8207','/opt/jdk-25.0.4/bin/java',{404614})
 child=actor_proof(404614,4248757,'729f697f456c7eeae55fe8eea6afd4638653bf3c075acba7d4e67e0fcd844b44','/usr/bin/python3.14',set())
 require(int((pathlib.Path('/proc/404614/stat').read_text().rpartition(')')[2].split()[1]))==404585)
 locks={};proc=pathlib.Path('/proc/404585')
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();m=md(p)
  require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(p))
  links=[]
  for f in (proc/'fd').iterdir():
   try:
    if str(f.readlink())==str(p):links.append(f.name)
   except FileNotFoundError:pass
  expected_fds={'maintenance.lock':{'30':'012400000','33':'012400000','34':'02100000'},
                'startup-admission.lock':{'43':'02100000','128':'02100000'}}[name]
  require(set(links)==set(expected_fds))
  for number in links:
   record=(proc/'fdinfo'/number).read_text()
   require(record.split('flags:')[1].splitlines()[0].strip()==expected_fds[number])
   held=(proc/'fd'/number).stat()
   require([held.st_dev,held.st_ino,held.st_uid,held.st_gid,held.st_mode,held.st_nlink,held.st_size,held.st_mtime_ns,held.st_ctime_ns]==m)
  matched=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   v=line.split()
   if len(v)>=8 and v[1:4]==['FLOCK','ADVISORY','WRITE']:
    d=v[5].split(':')
    if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matched.append(v[4])
  require(matched==['404585']);locks[name]={'metadata':m,'fds':expected_fds}
  require(md(p)==m)
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1134-issued-api-tools-v3')
 directories={p.as_posix()for n in FILES for p in pathlib.PurePosixPath(n).parents if p.as_posix()!='.'}
 require({p.relative_to(root).as_posix()for p in root.rglob('*')}==set(FILES)|directories)
 for p in [root,*root.rglob('*')]:
  s=p.lstat();require(not p.is_symlink()and s.st_uid==s.st_gid==0 and not os.listxattr(p))
  if p.is_dir():require(stat.S_IMODE(s.st_mode)==0o700)
  else:require(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o400 and hashlib.sha256(p.read_bytes()).hexdigest()==FILES[p.relative_to(root).as_posix()])
 error=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1134-issued-api-recovery-v1/refs.private.err').read_bytes()
 require(hashlib.sha256(error).hexdigest()=='990248fc7d68f5c739c6ed3354b3c9e1f0df15c461b9de6145ceffc3535e246b')
 names=[]
 for n in daemon.ListNames():
  if str(n).startswith(':'):
   try:
    if int(daemon.GetConnectionUnixProcessID(n))==404614:names.append(str(n))
   except dbus.DBusException:pass
 require(len(names)==1 and int(daemon.GetConnectionUnixUser(names[0]))==0)
 resource_zero()
 return {'java':java,'child':child,'locks':locks,'childBus':names[0],'databaseCurrent0':True,'oldNormalClose':False}
def whole():return {'current':capture(),'owner':owner()}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');refs=[]
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 observed=whole();require(observed==whole())
 SAVE.mkdir(mode=0o700)
 for name,value in [('observed.private.json',observed),('raw-journals.private.json',JOURNAL_READS)]:
  with(SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 require(observed==whole())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateSnapshotSha256':hashlib.sha256((SAVE/'observed.private.json').read_bytes()).hexdigest(),'scope':'READ_ONLY_FIXED_UNKNOWN_OWNER_PREFLIGHT','metadataRefsReturned':True,'oldOperationNormalClose':False,'signals0':True,'dbPeersAdvisory0':True,'actualBrokerAlreadyStopped':True,'expiryTwoStateDeltaVerified':True,'originalsDbBackupSourceUnchanged':True,'formalAccepted':False}))
'''


def main():
    raw=inspect.getsource(transport.main)
    raw=raw.replace('pg1120-current-failed-capture-v1','pg1141-failed-owner-preflight-v1').replace('PG1120-current-failed-capture-v1','PG1141-failed-owner-preflight-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(raw,'<fixed read-only old owner preflight>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
