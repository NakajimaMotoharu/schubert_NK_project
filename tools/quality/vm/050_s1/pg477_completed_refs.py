"""Fixed new-owner metadata lease after authenticated SSC191 handoff. No deployment/start/permit."""
import ast,json,os,pathlib,subprocess,stat,sys,time
import dbus
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg475-native-tools-v1')
from pg466_term_witness import FIELDS
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1')
UNITS=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
def require(value):
 if not value:raise ValueError('fixed Unit metadata/configuration refused')
def command(args,timeout=5):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=timeout)
 require(p.returncode==0 and len(p.stdout)<=1048576);return p.stdout
def show(unit,fields=FIELDS):
 require(unit in UNITS);rows=command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(fields))]).decode('ascii').splitlines();value={}
 for row in rows:
  key,text=row.split('=',1);require(key not in value);value[key]=text
 require(set(value)==fields)
 if 'Id' in fields:require(value['Id']==unit and value['LoadState']=='loaded')
 return value
def holder():
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);args=(p/'cmdline').read_bytes().split(b'\0')
 require(args[0]==b'/opt/jdk-25.0.4/bin/java' and args[-3:]==[b'Pg477CompletedAcceptance',sys.argv[1].encode(),b''])
 tick=int((p/'stat').read_text().rpartition(')')[2].split()[19]);fdpaths=[]
 for fd in (p/'fd').iterdir():
  try:fdpaths.append(str(fd.readlink()))
  except FileNotFoundError:continue
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;s=path.lstat()
  require(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and str(path) in fdpaths)
  hits=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   fs=line.split()
   if len(fs)>=8 and fs[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    d=fs[5].split(':')
    if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):hits.append(line)
  require(len(hits)==1)
 return pid,tick
def kernel(unit):
 p=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
 if p.exists():
  for d in [p,*[x for x in p.rglob('*') if x.is_dir()]]:
   require(not (d/'cgroup.procs').read_text().strip() and 'populated 0\n' in (d/'cgroup.events').read_text())

def policy():
    import re
    tree=ast.parse((TOOLS/'pg477_unit_references.py').read_text())
    config=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONFIG' for t in n.targets))
    names=['exec_record','after_exec','same_declaration','signed_declaration','effective_rw']
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];require(len(functions)==5)
    env={'re':re};exec(compile(ast.Module(body=[config,*functions],type_ignores=[]),'<fixed completed policy>','exec'),env);return env
def check():
    require(holder()==owner)
    require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54')
    result={}
    for unit in UNITS:
        v=show(unit);require(v['MainPID']==v['ControlPID']=='0' and not v['Job']);kernel(unit);require(v==show(unit));result[unit]=v
        conf=show(unit,rules['CONFIG']);old=proof['configuration'][unit]
        allowed={'ExecStart','DropInPaths','ReadWritePaths'} if unit in ['schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service','schubert-nk-morning-controller.service'] else {'ExecStart'}
        require(all(conf[k]==old[k] for k in rules['CONFIG']-allowed))
        require(rules['signed_declaration'](unit,old['ExecStart'],conf['ExecStart']))
        if len(allowed)>1:
            require(rules['effective_rw'](unit,old['ReadWritePaths'],conf['ReadWritePaths']))
            expected='/etc/systemd/system/'+unit+'.d/pg477-native-coverage.conf' if 'morning' in unit else ''
            require(conf['DropInPaths']==expected)
    require(result==proof['stopped']);return result
phase='PREFLIGHT';bus=None;refs=[]
try:
    require(os.geteuid()==0 and sys.argv[1:]==['verify'])
    for pid in [3412034,3412055,3413981]:require(not (pathlib.Path('/proc')/str(pid)).exists())
    require(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-partial-handoff-v3/interrupted.private').read_text()=='oldOperationInterrupted=true\nexpectedExit143=true\noldCloseUnknown=true\npartialCurrentNotReplayed=true\nnewOwnershipRequired=true\n')
    owner=holder();proof=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3/refs-activate-before.private.json').read_text());rules=policy()
    bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    phase='REF_ACQUIRE'
    for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
    before=check();print('REF_READY',flush=True)
    for line in sys.stdin.buffer:
        if line==b'check\n':require(check()==before);print('REF_CHECKED',flush=True)
        elif line==b'release\n':
            phase='REF_RELEASE';require(check()==before)
            for unit in reversed(refs):manager.UnrefUnit(unit)
            bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
        else:raise ValueError('fixed completed protocol refused')
    raise ValueError('completed owner channel ended early')
except Exception:
    print('REF_FAILED',flush=True);print('PG477_COMPLETED_REFERENCE_UNKNOWN phase='+phase+' senderRetained=true',file=sys.stderr,flush=True)
    while True:time.sleep(1)
