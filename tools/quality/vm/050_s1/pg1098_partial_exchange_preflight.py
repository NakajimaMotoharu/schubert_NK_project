"""SSC251 fixed16222/16248 read-only preflight; no lifecycle/publication authority."""
import ast
import hashlib
import json
from pathlib import Path
from pg1041_cold_policy_diagnostic import W
from pg1050_cold_tree_preflight import BODY as OLD
from pg1051_cold_tree_preflight_v2 import dispatch

HERE=Path(__file__).resolve().parent
PARENT_ARGV='8df52e97210dd41650da536a037da7b2647f6851c764973e8f0810b160d7f788'
CHILD_ARGV='4f134149ae07696304143818530e6ec17b9948a3c1b2f9b4d943a5bd28bbc04c'
ERROR='1b183218bcbef8ef17e7adba05b1a360c76ccd0956303c36ff32fdc0de109fa1'


def payload():
    frozen=json.loads((W/'pg1095-cold-activation-frozen-v2.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['operatorSource']!='b73a8bd2ce02d7f8d9072248c7cb51822dc7f3db':
        raise ValueError('fixed failed activation source required')
    root=W/'pg1094-cold-tools-v1'
    for n,d in frozen['fileHashes'].items():
        if hashlib.sha256((root/n).read_bytes()).hexdigest()!=d:raise ValueError('old failed operator payload changed')
    constants={'CHECKSUM_HASH','CONTRACT_SOURCE','LOCK_SOURCE','MANIFEST_SIZE','BOOT','SOURCE','BASELINE_HASH','BOM','PIN_HASH','SIG_HASH','CONFIG_FIELDS','RELEASE','FIELDS'}
    functions={'configuration_value','complete_configuration','require','command','metadata','tree','show','cold','snapshot','exec_record','same','controls','owned_peer_sql'}
    nodes=[]
    for n in ast.parse((root/'pg1094_cold_refs.py').read_bytes()).body:
        if isinstance(n,(ast.Import,ast.ImportFrom)):nodes.append(n)
        elif isinstance(n,ast.FunctionDef) and n.name in functions:nodes.append(n)
        elif isinstance(n,ast.Assign) and all(isinstance(t,ast.Name)for t in n.targets) and {t.id for t in n.targets}<=constants:nodes.append(n)
    fixed=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    helpers=[]
    for n in ast.parse(OLD).body:
        if isinstance(n,ast.FunctionDef) and n.name in ('actor','peer','safe'):
            s=ast.unparse(n).replace('5463','16222')
            helpers.append(s)
    modules={n:(HERE/f).read_text()for n,f in [('PUB','pg1083_cold_publication_contract.py'),('IO','pg1090_cold_finite_capture.py'),('EXCHANGE','pg1088_cold_exchange_io.py'),('SOCKET','pg1054_cold_socket_contract.py'),('PARTIAL','pg1097_partial_exchange_contract.py')]}
    # Embedded partial module resolves its explicitly frozen finite module.
    modules['PARTIAL']=modules['PARTIAL'].replace('from pg1083_cold_publication_contract import CURRENT,OLD_LINK,verify,verify_retained','CURRENT=pub.CURRENT;OLD_LINK=pub.OLD_LINK;verify=pub.verify;verify_retained=pub.verify_retained')
    prefix='FIXED='+repr(fixed)+'\nPINS='+repr(frozen['fileHashes'])+'\nMODULES='+repr(modules)+'\n'
    prefix+='PARENT_ARGV='+repr(PARENT_ARGV)+'\nCHILD_ARGV='+repr(CHILD_ARGV)+'\nERROR='+repr(ERROR)+'\n'
    raw=prefix+SETUP+'\n'+'\n'.join(helpers)+'\n'+BODY
    ast.parse(raw);return raw


SETUP=r'''
import ast,pathlib,os,hashlib,json,types,traceback,dbus,time,stat,subprocess
os.umask(0o077);assert os.geteuid()==0
env={};exec(FIXED,env)
def module(name,text,extra=None):
 m=types.ModuleType(name)
 if extra:m.__dict__.update(extra)
 exec(text,m.__dict__);return m
pub=module('finite',MODULES['PUB']);io=module('capture',MODULES['IO']);exchange_io=module('exchange',MODULES['EXCHANGE'])
partial=module('partial',MODULES['PARTIAL'],{'pub':pub});socket_module=module('socket',MODULES['SOCKET'])
contract=module('inventory',env['CONTRACT_SOURCE']);locks=module('locks',env['LOCK_SOURCE'])
env['contract']=contract;env['owned_flocks']=locks.owned_flocks;env['pub']=pub;env['PHASE']='after'
env['old']=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg989-bootstrap-post-v4/after.private.json').read_bytes())
prepared_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1062-cold-prepared-v1/after.private.json').read_bytes()
assert hashlib.sha256(prepared_raw).hexdigest()=='412eb77968cd3f28d5bf2869df52b3625233809ba119b2b90cf9080e976516bf'
prepared=json.loads(prepared_raw);sealed=prepared['snapshot']
OLD_SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1094-cold-activate-v1')
before_raw=(OLD_SAVE/'before.private.json').read_bytes();original_before=json.loads(before_raw)
begin_ns=1791631563504517000
# Bound below by the actual transport stage end, before activation started.
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==env['BOOT']
epoch=(OLD_SAVE/'new-epoch.private').read_bytes();assert epoch==pub.epoch_bytes(epoch.decode('ascii').splitlines()[3].removeprefix('epoch_id='))
query="select pid from pg_stat_activity where datname='schubert_nk'and usename='schubert_batch'and application_name='PG243-cold-empty'and backend_type='client backend';"
peers=env['command'](['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',query],4096).splitlines()
assert len(peers)==1 and peers[0].isdigit();env['OWNER_BACKEND']=int(peers[0]);env['OWNER_PID']=16222
expected_runtime=json.loads((OLD_SAVE/'approval.private.json').read_bytes())['runtime']
def runtime():
 root=pathlib.Path('/run/schubert-nk')
 v={k:env['metadata'](root if k=='@root'else root/k)for k in expected_runtime}
 assert v==expected_runtime
 assert set(os.listdir(root))=={'maintenance.lock','startup-admission.lock','maintenance','startup','backup-request','cleanup-request','expiry-request','pt-coverage'}
 for k in v:
  p=root if k=='@root'else root/k;assert not os.listxattr(p)
  if k=='startup':assert os.listdir(p)==['epoch.current'] and (p/'epoch.current').read_bytes()==epoch
  elif k not in ('@root','pt-coverage'):assert not os.listdir(p)
 assert set(os.listdir(root/'pt-coverage'))=={'parent','cleanup','expiry','root-api','backup','inspector'}
 return v
env['runtime_namespaces']=runtime
save=OLD_SAVE/'partial-preflight-v1';assert not os.path.lexists(save);save.mkdir(mode=0o700)
held=[];refs=[];bus=None;manager=None;phase='ENTRY';old_approval_fd=None
def retain(failure):
 print(json.dumps({'run':'PG1098-partial-exchange-preflight-v1','phase':phase,'type':type(failure).__name__,'ownershipRetained':True,'formalAccepted':False}),flush=True)
 for f in traceback.extract_tb(failure.__traceback__)[-4:]:print(json.dumps({'safeFrame':f.name,'line':f.lineno,'file':pathlib.Path(f.filename).name}),flush=True)
 while True:time.sleep(1)
def pin(path,digest):
 h=contract.HeldInventory(str(path.parent),[{'path':path.name,'size':path.stat().st_size,'sha256':digest}],0).open_file();held.append(h);return h
def inventory(root,records):
 h=contract.HeldInventory(str(root),records,0).open();held.append(h)
def release(root,bom,source):
 raw=(root/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==bom
 data=json.loads(raw);assert data['source']['commit']==source and len(data['artifacts'])==187 and len(data['migrations'])==29
 sums=contract.canonical_sum_bytes(data['artifacts'],bom);assert(root/'SHA256SUMS').read_bytes()==sums
 inventory(root,data['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':len(raw),'sha256':bom},{'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()}])
 for p in root.rglob('*'):
  if p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==(bom if p.name=='RELEASE-MANIFEST.json'else hashlib.sha256(sums).hexdigest()if p.name=='SHA256SUMS'else next(r['sha256']for r in data['artifacts']if r['path']==p.relative_to(root).as_posix()))
 sig=pathlib.Path('/var/lib/pgpt-s1-preservation/'+('pg932'if source==env['SOURCE']else'pg1068')+'-manifest.sig')
 subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(root/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 flags=env['command'](['findmnt','--target',str(root),'--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',');assert 'ro'in flags and 'rw'not in flags
'''


BODY=r'''
def tree_identity():
 parent=actor(16222,3020295,PARENT_ARGV,'/opt/jdk-25.0.4/bin/java',{16248})
 child=actor(16248,3020358,CHILD_ARGV,'/usr/bin/python3.14',set(),16222)
 locks={n:env['metadata'](pathlib.Path('/run/schubert-nk')/n)for n in ('maintenance.lock','startup-admission.lock')}
 env['owned_flocks'](pathlib.Path('/proc/locks').read_text().splitlines(),locks,16222)
 return {'parent':parent,'child':child,'locks':locks}
def read():
 first=tree_identity();server=peer();controls=env['controls']();snapshot=env['snapshot']()
 assert all(snapshot[k]==sealed[k]for k in ('units','rows','durable','artifacts'))
 for n,v in snapshot['configuration'].items():assert env['same'](sealed['configuration'][n],v,env['exec_record'])
 trees={r:io.direct_tree(r)for r in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)}
 partial.partial(original_before['trees'],trees,epoch,begin_ns,time.time_ns())
 original_row=original_before['trees'][pub.APPROVAL][pub.APPROVAL+'/current']
 pub.verify_retained(pub.APPROVAL+'/current',original_row,io.fd_record(old_approval_fd),'after',trees,begin_ns,time.time_ns())
 assert first==tree_identity() and server==peer() and controls==env['controls']()
 return {'tree':first,'server':server,'controls':controls,'snapshot':snapshot,'runtime':runtime(),'partialTrees':trees,'heldWholeMetadata':safe([h.capture()for h in held])}
try:
 phase='FIXED_TREE';tree_identity();peer();env['controls']();runtime()
 assert (OLD_SAVE/'refs.private.log').read_bytes()==b'PG1094_REFS_UNKNOWN phase=EXCHANGE type=ValueError ownershipRetained=true\n'
 assert not os.path.lexists(OLD_SAVE/'current-link.private') and not os.path.lexists(OLD_SAVE/'after.private.json')
 phase='SIGNED_HELD'
 original_row=original_before['trees'][pub.APPROVAL][pub.APPROVAL+'/current']
 aliases=[]
 for f in pathlib.Path('/proc/16248/fd').iterdir():
  m=io.metadata(f.stat())
  if m[:2]==original_row['metadata'][:2]:aliases.append(f)
 assert len(aliases)==1
 old_approval_fd=os.open(aliases[0],os.O_RDONLY|os.O_NONBLOCK)
 pub.verify_retained(pub.APPROVAL+'/current',original_row,io.fd_record(old_approval_fd),'after',
                    {r:io.direct_tree(r)for r in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)},begin_ns,time.time_ns())
 release(pathlib.Path(pub.OLD_LINK),env['BOM'],env['SOURCE'])
 release(pathlib.Path(pub.NEW_LINK),'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','d5b00104280028d9ea81b44c1d1c805f3c2861ed')
 for name,digest in [('pin.der',env['PIN_HASH'])]:pin(pathlib.Path('/etc/schubert-nk/deployment-key')/name,digest)
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig'),env['SIG_HASH'])
 pin(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig'),'5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b')
 pin(pathlib.Path(pub.APPROVAL)/'current',hashlib.sha256(pub.NEW_APPROVAL).hexdigest())
 tool=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1094-cold-tools-v1');raw=(tool/'payload-sha256.json').read_bytes();assert json.loads(raw)==PINS
 inventory(tool,[{'path':n,'size':(tool/n).stat().st_size,'sha256':d}for n,d in PINS.items()]+[{'path':'payload-sha256.json','size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}])
 for name in ('before.private.json','epoch.private.json','approval.private.json','new-epoch.private','old-approval.private','old-current.private','refs.private.log'):
  path=OLD_SAVE/name;pin(path,ERROR if name=='refs.private.log'else hashlib.sha256(path.read_bytes()).hexdigest())
 phase='TEN_REFS';bus=dbus.SystemBus(private=True)
 manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 child_names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==16248]
 assert len(child_names)==1 and int(daemon.GetConnectionUnixUser(child_names[0]))==0
 for name in env['old']['units']:manager.LoadUnit(name);manager.RefUnit(name);refs.append(name)
 phase='WHOLE_TWO_READ';before=read();assert before==read();before['childBusUniqueName']=child_names[0]
 private=json.dumps(before,sort_keys=True).encode()
 with(save/'before.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 phase='NORMAL_CLOSE'
 for name in reversed(refs):manager.UnrefUnit(name)
 bus.close()
 os.close(old_approval_fd)
 for h in reversed(held):h.close()
except BaseException as failure:retain(failure)
print(json.dumps({'run':'PG1098-partial-exchange-preflight-v1','actualExit':0,'oldActorUntouched':True,'signalAttempted':False,'oldNormalClose':False,'sameReadOnlyPeerSocket':True,'allOriginalsUnchangedTwice':True,'fullOldNewSigned':True,'partialPublicationVerified':True,'observerNormalClose':True,'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'formalAccepted':False}))
'''


if __name__=='__main__':dispatch('PG1098-partial-exchange-preflight-v1','pg1098-partial-exchange-preflight-v1',payload())
