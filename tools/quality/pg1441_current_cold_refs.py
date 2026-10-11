"""Build the fixed current child framing/FD observer; never dispatch on import."""
import ast
import inspect
from pathlib import Path
import sys

R=Path(__file__).resolve().parent/'vm/050_s1'
sys.path.insert(0,str(R))
import pg1026_cold_observation_contract as inventory
from pg1033_cold_handoff_preflight_v6 import payload as old_preflight
from pg1440_current_cold_identity_v4 import payload as current


def source():
    tree=ast.parse(current())
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    keep={'configuration_value','complete_configuration','require','command','metadata','tree','show','cold','exec_record','snapshot'}
    nodes=[]
    for n in tree.body:
        if isinstance(n,(ast.Import,ast.ImportFrom)):nodes.append(n)
        elif isinstance(n,ast.FunctionDef) and n.name in keep:nodes.append(n)
        elif isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) for t in n.targets):
            names={t.id for t in n.targets}
            if names<= {'CAPTURE_BOUND','UNIT_VECTOR','CONFIG_CONTRACT','CONFIG_FIELDS','BOOT','SOURCE','BOM','BASELINE','BASE','raw','old','UNITS','FIELDS'}:
                nodes.append(n)
        elif (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
              and isinstance(n.value.func,ast.Name) and n.value.func.id=='exec'
              and len(n.value.args)==2 and isinstance(n.value.args[1],ast.Name)
              and n.value.args[1].id in {'CAPTURE_BOUND','UNIT_VECTOR','CONFIG_CONTRACT'}):
            nodes.append(n)
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    # Current SQL table guard remains read-only. The one dedicated authenticated
    # caller is admitted during this metadata observer, not other app clients.
    marker="require(peers.splitlines() == [b'0', b'0'])"
    assert raw.count(marker)==1
    raw=raw.replace(marker,'peer_check()')
    old="for p in ['/run/schubert-nk/startup', '/run/schubert-nk/pt-coverage', '/var/lib/schubert-nk/maintenance/active']:\n        require(not os.path.lexists(p))"
    assert raw.count(old)==1
    raw=raw.replace(old,"require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active'))\n    runtime_check()")
    assignment=next(n for n in ast.parse(old_preflight()).body if isinstance(n,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id=='LOCK_SOURCE' for t in n.targets))
    prefix='INVENTORY_SOURCE='+repr(inspect.getsource(inventory))+'\nLOCK_SOURCE='+repr(ast.literal_eval(assignment.value))+'\n'
    raw=prefix+raw+'\n'+BODY
    ast.parse(raw);return raw


BODY=r'''
import dbus,time,sys,types
os.umask(0o077);require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='verify' and sys.argv[2].isdigit())
BACKEND=int(sys.argv[2]);require(1<BACKEND<2147483647)
PID=os.getppid();phase='ENTRY';PREPARED=False;PEER_CLOSED=False
SAVE=BASE/'pg1441-current-cold-prepared-v1'
require(metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2])
contract=types.ModuleType('held_inventory');exec(INVENTORY_SOURCE,contract.__dict__)
locks=types.ModuleType('lock_contract');exec(LOCK_SOURCE,locks.__dict__)
bus=None;refs=[];held=[];before_inventory=None;before_runtime=None;prepared_runtime=None;fixed_parent=None
ROOT=pathlib.Path('/run/schubert-nk')
ROLE_IDS={'backup':(992,977),'cleanup':(0,0),'expiry':(0,0),'inspector':(991,976),
 'ordinary-api193':(999,981),'ordinary-bootstrap196':(999,981),'ordinary-inspector196':(991,976),
 'ordinary-web193':(997,980),'parent':(0,0),'root-api':(0,0),'root-api193':(0,0),'root-web193':(0,0)}
NEW={'startup','backup-request','cleanup-request','expiry-request','pt-coverage'}
def actor():
 p=pathlib.Path('/proc')/str(PID);status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java')
 argv=(p/'cmdline').read_bytes();require(argv.split(b'\0')[-3:]==[b'Pg1441CurrentColdPreparation',b'prepare',b''])
 require({int(x)for task in(p/'task').iterdir()for x in(task/'children').read_text().split()}=={os.getpid()})
 metas={name:metadata(ROOT/name) for name in ['maintenance.lock','startup-admission.lock']}
 locks.owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),metas,PID)
 return {'pid':PID,'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),
         'argvSha256':hashlib.sha256(argv).hexdigest(),'locks':metas}
def peer_check():
 if PEER_CLOSED:
  sql=contract.all_client_sql(0)+"select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
  expected=[b'0',b'0']
 else:
  sql=contract.all_client_sql(BACKEND)+"select count(*)from pg_stat_activity where pid="+str(BACKEND)+" and datname='schubert_nk'and usename='schubert_batch'and application_name='PG243-cold-empty'and state in('active','idle in transaction')and exists(select 1 from pg_locks where pid="+str(BACKEND)+" and locktype='advisory'and classid=0 and objid=71419602 and granted);select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted and pid<>"+str(BACKEND)+";"
  expected=[b'0',b'1',b'0']
 value=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096)
 require(value.splitlines()==expected)
def runtime_check():
 global before_runtime,prepared_runtime
 entries=set(os.listdir(ROOT));fixed={'maintenance.lock','startup-admission.lock','maintenance'}
 m=metadata(ROOT);require(m[2:5]==[0,0,stat.S_IFDIR|0o755] and not os.listxattr(ROOT))
 if not PREPARED:
  require(entries==fixed)
  value={name:metadata(ROOT/name)for name in fixed};value['@root']=m
  require(value['maintenance'][2:6]==[0,0,stat.S_IFDIR|0o700,2] and not os.listdir(ROOT/'maintenance') and not os.listxattr(ROOT/'maintenance'))
  if before_runtime is None:before_runtime=value
  require(before_runtime==value)
 else:
  require(entries==fixed|NEW and before_runtime is not None)
  for name in fixed:require(metadata(ROOT/name)==before_runtime[name])
  require(m[:6]==before_runtime['@root'][:5]+[before_runtime['@root'][5]+5])
  for name in NEW:
   p=ROOT/name;v=metadata(p)
   require(v[2:6]==[0,0,stat.S_IFDIR|(0o755 if name=='pt-coverage'else 0o700),14 if name=='pt-coverage'else 2] and not os.listxattr(p))
   require(set(os.listdir(p))==(set(ROLE_IDS)if name=='pt-coverage'else set()))
  for role,(uid,gid)in ROLE_IDS.items():
   p=ROOT/'pt-coverage'/role
   require(metadata(p)[2:6]==[uid,gid,stat.S_IFDIR|0o700,2] and not os.listdir(p) and not os.listxattr(p))
  current={name:metadata(ROOT/name)for name in entries};current['@root']=m
  current['children']={role:metadata(ROOT/'pt-coverage'/role)for role in ROLE_IDS}
  if prepared_runtime is None:prepared_runtime=current
  require(prepared_runtime==current)
def inventory_check():
 value=[h.capture()for h in held];require(value==before_inventory)
 require(actor()==fixed_parent)
def framing(text):
 sys.stdout.write(text+'\n');sys.stdout.flush()
def retain(failure):
 sys.stderr.write('PG1441_REFS_UNKNOWN phase='+phase+' type='+type(failure).__name__+' ownershipRetained=true\n');sys.stderr.flush()
 while True:time.sleep(1)
try:
 phase='BEFORE_HELD_SIGNATURE'
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
 manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM)
 data=json.loads(manifest)
 records=data['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':len(manifest),'sha256':BOM}]
 sums=contract.canonical_sum_bytes(data['artifacts'],BOM)
 require((release/'SHA256SUMS').read_bytes()==sums)
 records.append({'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()})
 require('VERSION'in {record['path']for record in data['artifacts']})
 held.append(contract.HeldInventory(str(release),records,0).open())
 for path,size,digest in [
  (pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),44,'3378dbf29039d9fd0194f8c949a8793f00aff460bfeb6c69aba492498f4de221'),
  (BASE/'pg1292-manifest.sig',64,'97fd4c41a795c5f2465cf2f5074831723db0c3942fa8d62d16a5aad54cb318f7'),
  (pathlib.Path('/etc/schubert-nk/release-approval/current'),116,None)]:
  body=path.read_bytes()
  if digest is None:
   expected=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256='+BOM+'\n').encode()
   require(body==expected);size=len(expected);digest=hashlib.sha256(expected).hexdigest()
  require(len(body)==size and hashlib.sha256(body).hexdigest()==digest)
  held.append(contract.HeldInventory(str(path.parent),[{'path':path.name,'size':size,'sha256':digest}],0).open_file())
 before_inventory=[h.capture()for h in held];fixed_parent=actor()
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in UNITS:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 phase='BEFORE_FULL_TWO';first=snapshot();require(first==snapshot());inventory_check();framing('REF_READY')
 for line in sys.stdin:
  action=line.strip()
  require(action in {'prepare','prepared','run','release'})
  if action=='prepared':PREPARED=True
  if action=='run':PEER_CLOSED=True
  phase='FULL_'+action.upper()
  current=snapshot();require(current==snapshot());inventory_check()
  if PREPARED:
   opts=command(['findmnt','--target',str(release),'--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',')
   require('ro'in opts and 'rw'not in opts)
  if action=='release':
   require(PREPARED and PEER_CLOSED)
   for name in reversed(refs):manager.UnrefUnit(name)
   refs=[];bus.close();bus=None
   for h in reversed(held):h.close()
   held=[]
   encoded=json.dumps({'current':current,'runtime':prepared_runtime,'parent':fixed_parent},sort_keys=True).encode()
   with(SAVE/'after.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
   framing('REF_RELEASED');break
  framing('REF_CHECKED')
 else:raise ValueError('cold framing incomplete')
except BaseException as failure:retain(failure)
'''


if __name__=='__main__':
    print('CURRENT_COLD_REF_SOURCE_BUILT_NO_ACTION',len(source()))
