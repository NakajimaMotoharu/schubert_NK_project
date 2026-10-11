"""Current fullguard turned into finite one-role retained-reference protocol."""
import ast
import inspect
import json
from pathlib import Path
import pg1340_published_stop_independent_post_v4 as guard
import pg1369_bootstrap_role_policy as policy
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

BASE='/var/lib/pgpt-s1-preservation/pg1344-current-bootstrap-before-v1/after.private.json'
BASE_SHA='f64ed4689d2c52e2227f771f7870414686ff0e6f52a6dc7b3d1b22313668428d'

OWNER=r'''
def holder(present):
 p=pathlib.Path('/proc')/str(parent);a=(p/'cmdline').read_bytes().split(b'\0');s=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
 require(a[0]==b'/opt/jdk-25.0.4/bin/java'and a[-3:]==[b'Pg1372BootstrapRolePreparation',b'prepare',b'']and str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'and s['Uid'].split()==s['Gid'].split()==['0']*4 and s['Groups'].split()==['0'])
 ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19]);links=[]
 for f in(p/'fd').iterdir():
  try:links.append(str(f.readlink()))
  except FileNotFoundError:continue
 for name in ('maintenance.lock','startup-admission.lock'):require('/run/schubert-nk/'+name in links)
 q="select count(*)from pg_stat_activity a where pid="+str(backend)+"and datname='schubert_nk'and usename='schubert_batch'and application_name='PG998-bootstrap-role'and client_addr=inet '127.0.0.1'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted);"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).strip()==(b'1'if present else b'0'))
 return (parent,ticks,hashlib.sha256((p/'cmdline').read_bytes()).hexdigest())
def declaration():
 u='schubert-nk-bootstrap-admin.service';values=complete_configuration(command(['systemctl','show',u,'--property='+','.join(sorted(FIELDS))]).decode(),u)
 require(show(u,{'LoadState','Type'})=={'LoadState':'loaded','Type':'oneshot'}and values['User']=='schubert-api'and values['Group']=='schubert-api'and '/run/schubert-nk/pt-coverage/ordinary-bootstrap196'in values['ReadWritePaths'].split())
 require('-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-'in values['ExecStart'])
 require(command(['id','-u','schubert-api']).strip()==b'999'and command(['id','-g','schubert-api']).strip()==b'981')
def save(name,value):
 raw=json.dumps(value,sort_keys=True).encode()
 with(SAVE/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''

BODY=r'''
require(len(sys.argv)==3 and sys.argv[1]=='prepare'and sys.argv[2].isdigit());backend=int(sys.argv[2]);parent=os.getppid()
SAVE=base/'pg1372-bootstrap-role-prepare-v1';require(SAVE.is_dir()and {p.name for p in SAVE.iterdir()}=={'refs.private.log'})
raw=strict(pathlib.Path(BASE),0o600,67108864);require(hashlib.sha256(raw).hexdigest()==BASE_SHA);baseline=json.loads(raw);prior=baseline['native'];policy.before_valid(prior)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 held=holder(True);declaration();initial=capture(True);require(initial==prior and initial==capture(True)and held==holder(True));save('before.private.json',{'current':after,'native':prior,'holder':held})
 print('REF_READY',flush=True);state='READY';lower=None;prepared=None
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n');require(held==holder(state!='CLOSED'));declaration()
  if action==b'before':
   require(state=='READY'and capture(True)==prior and held==holder(True));lower=time.time_ns();state='BEFORE';print('REF_CHECKED',flush=True)
  elif action==b'prepared':
   require(state=='BEFORE'and type(lower)is int);upper=time.time_ns();now=capture(True);require(now==capture(True));policy.delta(prior,now,lower,upper)
   role=pathlib.Path(policy.ROOT,policy.ROLE);require(not list(role.iterdir())and not os.listxattr(role)and command(['findmnt','--target',str(role),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
   prepared={'current':after,'native':now,'startNs':lower,'endNs':upper,'holder':held};save('prepared.private.json',prepared);state='PREPARED';print('REF_CHECKED',flush=True)
  elif action==b'closed':
   require(state=='PREPARED'and holder(False)==held and capture(False)==prepared['native']and capture(False)==prepared['native']);save('after.private.json',prepared);state='CLOSED';print('REF_CHECKED',flush=True)
  elif action==b'release':
   require(state=='CLOSED'and holder(False)==held and capture(False)==prepared['native']);break
  else:raise ValueError('fixed role phase refused')
 else:raise ValueError('fixed role owner channel ended')
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
require(state=='CLOSED');print('REF_RELEASED',flush=True)
'''

def helper():
    post=json.loads((W/'pg1340-published-terminal-post-v4.safe.json').read_bytes())
    seals={k:v['sha256']for k,v in post['proofHashes'].items()if k in guard.previous.transport.previous.SEALS}
    raw=guard.payload(seals);tree=ast.parse(raw)
    scope=next(n for n in tree.body if isinstance(n,ast.Try)and n.body and isinstance(n.body[0],ast.For))
    prefix=''.join(raw.splitlines(keepends=True)[:scope.lineno-1]);prefix=prefix[:prefix.index('bus=dbus.SystemBus(private=True);')]
    node=next(n for n in scope.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    node.name='capture';node.args.args=[ast.arg(arg='present')]
    capture=ast.unparse(node).replace("lines[-2:] == [b'0', b'0']","lines[-2:] == ([b'1', b'1'] if present else [b'0', b'0'])")
    old='require((int(d[0], 16), int(d[1], 16), int(d[2])) != (os.major(s.st_dev), os.minor(s.st_dev), s.st_ino))'
    if capture.count(old)!=1:raise ValueError('one actual owned M-A boundary required')
    capture=capture.replace(old,"\n                if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):require(f[1:5]==['FLOCK','ADVISORY','WRITE',str(parent)])")
    hashes=post['toolHashes'];receipt=(W/'pg1334-native-tools-v1/pg1334_parent_receipt.py').read_text()
    prefix='HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+prefix
    code=prefix+'\nBASE='+repr(BASE)+'\nBASE_SHA='+repr(BASE_SHA)+'\n'+capture+'\n'+OWNER
    code+='\nimport types,traceback\npolicy=types.ModuleType("one_role_policy");exec('+repr(inspect.getsource(policy))+',policy.__dict__)\n'
    # Any failed scope retains its own bus/Refs; parent owns M-A/DB and remains attached.
    body=BODY.replace('finally:\n for u in reversed(refs):',"except Exception as failure:\n print('REF_FAILED',flush=True);print('PG1372_REF_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)\n for frame in traceback.extract_tb(failure.__traceback__):\n  if frame.filename==__file__:print('PG1372_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)\n while True:time.sleep(1)\nfinally:\n for u in reversed(refs):")
    code+='\n'+body;ast.parse(code);return code

def files():
    return {'Pg1372BootstrapRolePreparation.java':Path(__file__).with_name('Pg1372BootstrapRolePreparation.java').read_text(),
            'pg1372_bootstrap_role_refs.py':helper()}
