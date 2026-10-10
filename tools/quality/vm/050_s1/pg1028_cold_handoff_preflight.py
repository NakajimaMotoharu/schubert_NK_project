"""SSC244 fixed no-DB old actor preflight ONLY. Never sends TERM or starts Units.

Existing Java3091 retains M/A throughout this observer. Any failed proof rejects
handoff; old UNKNOWN stays UNKNOWN. New observer close failures retain isolation.
"""
import ast
import hashlib
import json
from pathlib import Path
from pg1002_cold_readonly import capture
from pg1023_cold_readback_sources import guest as old_guest

HERE = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def payload():
    tree = ast.parse(old_guest())
    functions = {'require', 'command', 'metadata', 'tree', 'show', 'cold', 'snapshot',
                 'complete_configuration', 'exec_record', 'same'}
    constants = {'BOOT', 'SOURCE', 'BASELINE_HASH', 'BOM', 'PIN_HASH', 'SIG_HASH',
                 'CONFIG_FIELDS', 'RELEASE', 'FIELDS'}
    nodes = [n for n in tree.body if isinstance(n, ast.Import)
             or isinstance(n, ast.ImportFrom) and not (n.module or '').startswith('pg')
             or isinstance(n, ast.FunctionDef) and n.name in functions
             or isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id in constants for t in n.targets)]
    raw = ast.unparse(ast.Module(body=nodes, type_ignores=[]))
    frozen = json.loads((W / 'pg1024-cold-readback-frozen-v1.safe.json').read_bytes())
    if frozen['operatorSource'] != '5a8aacfc8d640b1ba47b88faa20b160ec6ed7699' or frozen['actualExit'] != 0:
        raise ValueError('fixed old source refused')
    manifest = (W / 'pg932-release-v1/RELEASE-MANIFEST.json').read_bytes()
    prefix = 'CONTRACT_SOURCE=' + repr((HERE / 'pg1026_cold_observation_contract.py').read_text()) + '\n'
    prefix += 'LOCK_SOURCE=' + repr((HERE / 'pg1023_cold_contract.py').read_text()) + '\n'
    prefix += 'PINS=' + repr(frozen['fileHashes']) + '\nMANIFEST_SIZE=' + repr(len(manifest)) + '\n'
    payload_bytes = (W / 'pg1023-cold-tools-v1/payload-sha256.json').read_bytes()
    if json.loads(payload_bytes) != frozen['fileHashes']:
        raise ValueError('frozen payload map refused')
    prefix += 'PAYLOAD_HASH=' + repr(hashlib.sha256(payload_bytes).hexdigest()) + '\nPAYLOAD_SIZE=' + repr(len(payload_bytes)) + '\n'
    code = prefix + raw + '\n' + BODY
    ast.parse(code)
    return code


BODY = r'''
import types,sys,time,dbus
contract=types.ModuleType('pg1026_fixed');exec(CONTRACT_SOURCE,contract.__dict__)
locks_module=types.ModuleType('pg1023_fixed');exec(LOCK_SOURCE,locks_module.__dict__)
owned_flocks=locks_module.owned_flocks
OWNER_PID=3091;OWNER_BACKEND=0
def owned_peer_sql(backend):
 require(backend==0)
 return (contract.all_client_sql(0)+"select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;select count(*)from pg_stat_activity where datname='schubert_nk'and pid=0;")
require(os.geteuid()==0)
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
require(pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01')
baseline=pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes()
require(hashlib.sha256(baseline).hexdigest()==BASELINE_HASH);old=json.loads(baseline)
sealed_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1004-cold-readonly-v3/after.private.json').read_bytes()
require(hashlib.sha256(sealed_raw).hexdigest()=='1cbb10fa83df138d5f3fe6b40b8107e16475e280745797f6e9e5a58d030073a9')
sealed=json.loads(sealed_raw)
save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1028-cold-handoff-preflight-v1')
require(not os.path.lexists(save));save.mkdir(mode=0o700)
held=[];refs=[];bus=None;manager=None;phase='ENTRY'
def hold_material(path,size,digest):
 h=contract.HeldInventory(str(path.parent),[{'path':path.name,'size':size,'sha256':digest}],0).open_file()
 held.append(h);m=h.capture()[-1][1];require(m[2:6]==(0,0,stat.S_IFREG|0o400,1));return h
def controls():
 result={}
 for name in ['timers.target','paths.target']:
  raw=command(['systemctl','show',name,'--property=LoadState,ActiveState,SubState,Job'],4096).decode()
  fields=dict(line.split('=',1)for line in raw.splitlines())
  require(fields=={'LoadState':'masked','ActiveState':'inactive','SubState':'dead','Job':''});result[name]=fields
 units=command(['systemctl','list-units','--all','--type=timer,path','--no-legend','--no-pager','--plain'],65536).decode()
 for line in units.splitlines():
  f=line.split();require(len(f)>=4 and f[2]not in ('active','activating','reloading')and f[3]not in ('waiting','running'))
 result['timerPathUnitsSha256']=hashlib.sha256(units.encode()).hexdigest()
 return result
def actor():
 p=pathlib.Path('/proc/3091')
 ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19]);require(ticks==835207)
 argv=hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()
 require(argv=='7e296d5389083bda25323521dae31089322d744291a66ed621aa25dea0d39dc5')
 require(str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java')
 status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 tasks=sorted((p/'task').iterdir());require(not {int(c)for t in tasks for c in(t/'children').read_text().split()})
 require(tasks==sorted((p/'task').iterdir()))
 lockmeta={n:metadata(pathlib.Path('/run/schubert-nk')/n)for n in ['maintenance.lock','startup-admission.lock']}
 owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),lockmeta,3091)
 actor_fd_locks=[]
 for fd in(p/'fd').iterdir():
  s=fd.stat()
  if any((s.st_dev,s.st_ino)==tuple(m[:2])for m in lockmeta.values()):
   actor_fd_locks.extend(l.removeprefix('lock:').strip()for l in(p/'fdinfo'/fd.name).read_text().splitlines()if l.startswith('lock:'))
 owned_flocks(actor_fd_locks,lockmeta,3091)
 partial=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1023-cold-owned-v1')
 require(not list(partial.iterdir()))
 return {'pid':3091,'ticks':ticks,'argvSha256':argv,'exe':str((p/'exe').readlink()),
  'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb')},
  'cgroup':(p/'cgroup').read_text(),'lockMetadata':lockmeta}
def tool_payload():
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1023-cold-tools-v1')
 require({p.name for p in root.iterdir()}==set(PINS)|{'payload-sha256.json'})
 require(json.loads((root/'payload-sha256.json').read_bytes())==PINS)
 # Pin all tool bytes and manifest metadata while existing Java remains alive.
 records=[{'path':n,'size':(root/n).stat().st_size,'sha256':d}for n,d in PINS.items()]
 records.append({'path':'payload-sha256.json','size':PAYLOAD_SIZE,'sha256':PAYLOAD_HASH})
 h=contract.HeldInventory(str(root),records,0).open();held.append(h)
 for _,m,_,_ in h.capture():
  if stat.S_ISREG(m[4]):require(m[2:6]==(0,0,stat.S_IFREG|0o400,1))
def safe_json(v):
 if isinstance(v,bytes):return {'bytesSha256':hashlib.sha256(v).hexdigest(),'length':len(v)}
 if isinstance(v,dict):return {k:safe_json(x)for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [safe_json(x)for x in v]
 return v
def read():
 a=actor();c=controls();v=snapshot()
 require(v['units']==sealed['units']and v['rows']==sealed['rows']and v['durable']==sealed['durable']and v['artifacts']==sealed['artifacts'])
 for name,value in v['configuration'].items():
  require(same(sealed['configuration'][name],value,exec_record))
  start=exec_record(value['ExecStart']);require(start is not None and start[3:]==('n/a','n/a','0','(null)','0/0'))
  require(value['ExecStop']=='')
 require(actor()==a and controls()==c)
 s=pathlib.Path('/opt/schubert-nk/current').lstat();require(stat.S_ISLNK(s.st_mode))
 return safe_json({'snapshot':v,'actor':a,'controls':c,'heldWholeMetadata':[h.capture()for h in held],
  'selectorMetadata':metadata(pathlib.Path('/opt/schubert-nk')),
  'selectorLinkMetadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]})
def retain(failure):
 print('PG1028_CLOSE_UNKNOWN phase='+phase+' type='+type(failure).__name__+' isolationRetained=true',file=sys.stderr,flush=True)
 while True:time.sleep(1)
try:
 phase='OLD_ACTOR_AND_EXCLUSION';actor();controls()
 phase='SIGNED_HELD_BYTES'
 manifest=(RELEASE/'RELEASE-MANIFEST.json').read_bytes();require(len(manifest)==MANIFEST_SIZE and hashlib.sha256(manifest).hexdigest()==BOM)
 records=json.loads(manifest)['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':MANIFEST_SIZE,'sha256':BOM}]
 h=contract.HeldInventory(str(RELEASE),records,0).open();held.append(h)
 hold_material(pathlib.Path('/etc/schubert-nk/deployment-key/pin.der'),44,PIN_HASH)
 hold_material(pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig'),64,SIG_HASH)
 approval=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG932\nmanifest_sha256='+BOM+'\n').encode()
 hold_material(pathlib.Path('/etc/schubert-nk/release-approval/current'),len(approval),hashlib.sha256(approval).hexdigest())
 tool_payload()
 phase='TEN_METADATA_REFS';bus=dbus.SystemBus(private=True)
 manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in old['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 phase='INDEPENDENT_TWO_READ';before=read();after=read();require(before==after)
except BaseException as failure:
 # No TERM or state mutation occurred. The old actor still owns M/A. Observer
 # scope may close normally, but a failed proof is never a handoff acceptance.
 failed=failure
else:failed=None
phase='OBSERVER_NORMAL_CLOSE'
try:
 for name in reversed(refs):manager.UnrefUnit(name)
 if bus is not None:bus.close()
 for h in reversed(held):h.close()
except BaseException as failure:retain(failure)
if failed is not None:
 print(json.dumps({'actualExit':1,'phase':'READONLY_PROOF_REFUSED','type':type(failed).__name__,'oldActorUntouched':True,'termSent':False}))
 raise SystemExit(1)
private=json.dumps(before,sort_keys=True).encode()
with(save/'before.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'run':'PG1028-cold-handoff-preflight-v1','actualExit':0,'boot':BOOT,'source':SOURCE,
 'oldActorPID':3091,'oldActorTicks':835207,'oldActorUntouched':True,'termSent':False,'all24RowsUnchangedTwice':True,
 'allTenColdFull32':True,'allSignedPayloadMetadataHeld':True,'allApplicationDBClients0':True,
 'currentTimerPathSuppression':True,'observerScopesReturnedNormally':True,'oldOperationNormalClose':False,
 'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'formalAccepted':False,'fullColdPreparationAccepted':False}))
'''


if __name__ == '__main__':
    capture('pg1028-cold-handoff-preflight-v1', payload())
